import { useState } from 'react'

// Shared input (footer + popup), spec §7.4. Label acts as the visual placeholder; `.js-focus` lifts it.
export default function Input({ id, label, required, validation, value, onChange, error, inputRef, className = '' }) {
  const [focused, setFocused] = useState(false)
  const lifted = focused || value.length > 0
  return (
    <div className={`input-content ${className}`.trim()}>
      <div className={`input-wrapper${lifted ? ' js-focus' : ''}`}>
        <input
          id={id}
          ref={inputRef}
          value={value}
          className="input"
          required={required}
          data-validation={required || validation ? 'required' : undefined}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        />
        <label htmlFor={id} className="input-placeholder">
          {label}{' '}
          {required && <abbr title="required"> * </abbr>}
        </label>
      </div>
      {error && <small className="input-error">{error}</small>}
    </div>
  )
}
