const ROLE_STYLES: Record<string, string> = {
  'Primary Finisher': 'bg-blue-900/40 text-sky-300',
  'Leverage Creator (Draws Calls)': 'bg-purple-900/40 text-purple-300',
  'Disruptor (Defense/Transition)': 'bg-green-900/40 text-green-300',
  'Goalie Anchor': 'bg-amber-900/40 text-amber-300',
}
const DEFAULT_STYLE = 'bg-slate-800 text-slate-400'

const ROLE_LABELS: Record<string, string> = {
  'Primary Finisher': 'Finisher',
  'Leverage Creator (Draws Calls)': 'Leverage Creator',
  'Disruptor (Defense/Transition)': 'Disruptor',
  'Goalie Anchor': 'Goalie Anchor',
}

interface Props {
  role: string
}

export default function RoleBadge({ role }: Props) {
  const style = ROLE_STYLES[role] ?? DEFAULT_STYLE
  const label = ROLE_LABELS[role] ?? role
  return (
    <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${style}`}>
      {label}
    </span>
  )
}
