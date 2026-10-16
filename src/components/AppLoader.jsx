import { useUI } from '../context.jsx'

// Form-submit spinner, spec §7.4 / §5.11. The CSS (.circular / .path keyframes) is original; the SVG geometry
// (viewBox 25 25 50 50, r=20, stroke-width 2) is NOT in the spec — it is the standard markup those keyframes target.
export default function AppLoader() {
  const { appLoading } = useUI()
  if (!appLoading) return null
  return (
    <div className="app-loader">
      <svg className="circular" viewBox="25 25 50 50">
        <circle className="path" cx="50" cy="50" r="20" fill="none" strokeWidth="2" strokeMiterlimit="10" />
      </svg>
    </div>
  )
}
