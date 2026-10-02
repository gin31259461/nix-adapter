# Presentation-only Bash adapter. Callers retain traps and subprocess ownership.
# Each bounded frame is acknowledged before another one is sent. Application
# stdin/stdout are never used for the renderer's control protocol.

progress_init() {
  progress_verbose=${2:-0}
  progress_event_fd='' progress_ack_fd='' progress_pid=''
  progress_sequence=0 progress_label='' progress_started=$SECONDS
  progress_interactive=0
  if [[ -t 2 && ${TERM:-dumb} != dumb && ! -v NO_COLOR && -z ${CI:-} && $progress_verbose == 0 ]]; then
    progress_interactive=1
  fi
  if [[ -n ${progress_renderer:-} && -x $progress_renderer ]]; then
    local args=(--renderer) event_source ack_source
    [[ $progress_verbose != 1 ]] || args+=(--verbose)
    coproc progress_worker { exec "$progress_renderer" "${args[@]}"; }
    progress_pid=${progress_worker_PID:-}
    event_source=${progress_worker[1]:-}
    ack_source=${progress_worker[0]:-}
    if [[ -n $event_source && -n $ack_source ]]; then
      { exec {progress_event_fd}>&"$event_source"; } 2>/dev/null || progress_event_fd=
      { exec {progress_ack_fd}<&"$ack_source"; } 2>/dev/null || progress_ack_fd=
      { exec {event_source}>&-; exec {ack_source}<&-; } 2>/dev/null || true
    fi
  fi
  return 0
}

_progress_shutdown() {
  if [[ -n ${progress_event_fd:-} ]]; then
    { exec {progress_event_fd}>&-; } 2>/dev/null || true
  fi
  if [[ -n ${progress_ack_fd:-} ]]; then
    { exec {progress_ack_fd}<&-; } 2>/dev/null || true
  fi
  progress_event_fd='' progress_ack_fd=''
  if [[ -n ${progress_pid:-} ]]; then
    # CONT also lets a stopped renderer handle TERM. Never wait indefinitely
    # for a display process while a workstation command is trying to exit.
    kill -TERM "$progress_pid" 2>/dev/null || true
    kill -CONT "$progress_pid" 2>/dev/null || true
    local attempt
    for ((attempt=0; attempt<5; attempt++)); do
      kill -0 "$progress_pid" 2>/dev/null || break
      sleep 0.02
    done
    kill -KILL "$progress_pid" 2>/dev/null || true
    wait "$progress_pid" 2>/dev/null || true
    progress_pid=
  fi
  return 0
}

_progress_exchange() {
  progress_delivered=0
  [[ -n ${progress_event_fd:-} && -n ${progress_ack_fd:-} ]] || return 0
  progress_sequence=$((progress_sequence + 1))
  local reply
  # A subshell contains SIGPIPE; a renderer failure must not kill the caller.
  if (printf '{"id":%s,%s}\n' "$progress_sequence" "$1" >&"$progress_event_fd") 2>/dev/null &&
    IFS= read -r -t 2 -u "$progress_ack_fd" reply 2>/dev/null &&
    [[ $reply == "$progress_sequence" ]]; then
    progress_delivered=1
  else
    _progress_shutdown
    if [[ ${progress_interactive:-0} == 1 ]]; then printf '\033[?25h' >&2; fi
  fi
  return 0
}

_progress_plain() {
  # Builtin fallback for a missing/broken renderer. Only the already-safe task
  # label and status enter this output, never a command or its arguments.
  printf '[%s] %s (%ss)\n' "$1" "${progress_label:-task}" "$((SECONDS - progress_started))" >&2 || true
  return 0
}

progress_start() {
  local label=${1:-task} total=${2:-} encoded
  [[ -z ${progress_label:-} ]] || progress_finish failed
  # Bound a frame below PIPE_BUF, so a stopped worker cannot block a write.
  progress_label=${label:0:512}
  progress_label=${progress_label//[[:cntrl:]]/ }
  progress_started=$SECONDS
  encoded=$(printf '%s' "$progress_label" | "${progress_base64:-base64}" -w0) || encoded=
  local fields="\"event\":\"start\",\"label_b64\":\"$encoded\""
  if [[ $total =~ ^(0|[1-9][0-9]{0,8})$ ]]; then fields+=",\"total\":$total"; fi
  _progress_exchange "$fields"
  [[ ${progress_delivered:-0} == 1 ]] || _progress_plain start
  return 0
}

progress_update() {
  local completed=${1:-0} total=${2:-}
  [[ $completed =~ ^(0|[1-9][0-9]{0,8})$ ]] || return 0
  local fields="\"event\":\"update\",\"completed\":$completed"
  if [[ $total =~ ^(0|[1-9][0-9]{0,8})$ ]]; then fields+=",\"total\":$total"; fi
  _progress_exchange "$fields"
  return 0
}

progress_finish() {
  [[ -n ${progress_label:-} ]] || return 0
  local status=${1:-done}
  case "$status" in done|skip|failed) ;; *) status=failed ;; esac
  _progress_exchange "\"event\":\"finish\",\"status\":\"$status\""
  [[ ${progress_delivered:-0} == 1 ]] || _progress_plain "$status"
  progress_label=
  return 0
}
progress_suspend() { _progress_exchange '"event":"suspend"'; return 0; }
progress_resume() { _progress_exchange '"event":"resume"'; return 0; }
progress_close() {
  [[ -z ${progress_label:-} ]] || progress_finish failed
  _progress_exchange '"event":"close"'
  _progress_shutdown
  return 0
}
progress_exit() {
  local status=failed
  [[ ${1:-1} != 0 ]] || status='done'
  progress_finish "$status"
  progress_close
  return 0
}
