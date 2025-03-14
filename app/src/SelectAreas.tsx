type SelectAreasProps = {
  id: string;
  name: string;
  className: string;
  toggleArea: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

export const SelectAreas = ({ toggleArea, className, id, name }: SelectAreasProps) => {
  return (
    <button
      type="button"
      className={`filter ${className}`}
      id={id}
      name={name}
      onClick={toggleArea}
    ><span id={name}>{name.toUpperCase()}</span></button>
  )
}