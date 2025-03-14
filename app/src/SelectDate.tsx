import { DateTime } from "luxon";
import { useState } from "react";

type SelectDateProps = {
  handleDateChange: (event: React.ChangeEvent<HTMLSelectElement>) => void
}
const generateUpcomingMonths = () => {
  const months = [];
  const today = DateTime.now().set({ day: 1, hour: 0, minute: 0, second: 0, millisecond: 0 });

  for (let i = 0; i < 6; i++) {
    const date = today.plus({ months: i });
    months.push({
      value: date.toISO(),
      label: date.setLocale("fr").toFormat("MMMM-yy"),
    });
  }

  return months;
};
export const SelectDate = ({ handleDateChange }: SelectDateProps) => {
  const [selectValue, setSelectValue] = useState('Choisir une date');
  const upcomingMonths = generateUpcomingMonths();

  const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    console.log("event.target.value - ", event.target.value);
    setSelectValue(event.target.value);
    handleDateChange(event);
  }
  return (
    <select
      id="monthSelect"
      onChange={handleSelectChange}
      value={selectValue}
    >
      <option className="month-option" aria-label="Choisir une date" label="Choisir une date" value="">Choisir
        une date</option>
      {upcomingMonths.map((month) => (
        <option className="month-option" key={month.value} value={month.value}>
          {month.label}
        </option>
      ))}
    </select>
  )
}