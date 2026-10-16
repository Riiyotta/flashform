// `.button` markup exactly as in the original: [ label ] with a hidden 4x marquee for hover (spec §5.13).
export default function Button({ as: Tag = 'button', className = '', children, ...rest }) {
  const label = children
  return (
    <Tag className={`button ${className}`.trim()} {...rest}>
      <span className="button__content-before">[</span>
      <span className="button__content">
        <span className="button__items">
          <span className="button__text">{label}</span>
          <span className="button__hover-text-wrapper">
            <span className="button__hover-text">{`${label} ${label} ${label} ${label}`}</span>
          </span>
        </span>
      </span>
      <span className="button__content-after">]</span>
    </Tag>
  )
}
