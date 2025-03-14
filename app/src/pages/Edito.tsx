// Init config from codebase
import './edito.css'
import { editoQuery, OA_SLUG, API_URL } from "../config";
// Import OpenAgenda types
import type { OpenAgendaEditoItem, OpenAgendaEditoResponse, OpenAgendaEventsReponse } from "../types/OpenAgenda";
// HTTP & query libs
import ky from "ky";
import { useQuery } from "@tanstack/react-query";
import { ImSpinner7 } from "react-icons/im";

// Table lib
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

// Tag input lib
// FIXME: Use a more customizable lib
// Prefer https://use-bootstrap-tag.js.org/demo.html?
import TagInput from 'rsuite/TagInput'
import "rsuite/dist/rsuite-no-reset.min.css";

// React stuff
import { useEffect, useState } from 'react';

const DATE_COLUMNS = ['firstTimingDate', 'firstTimingTimeStart', 'firstTimingTimeEnd']

const OaLinkCell = ({ getValue, row, column, table }) => {
  return (
    <a href={`https://openagenda.com/${OA_SLUG}/events/${getValue()}`} target="_blank" rel="noreferrer" tabIndex={-1}>
      {getValue()}
    </a>
  )
}

const ExtLinkCell = ({ getValue, row, column, table }) => {
  const regex = /^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:/\n?]+)/i
  const linkText = getValue()?.match(regex)?.[1]
  return (
    <a href={getValue()} target="_blank" rel="noreferrer" tabIndex={-1}>
      {linkText ?? getValue()}
    </a>
  )
}

const TableCell = ({ getValue, row, column, table }) => {
  const [value, setValue] = useState(getValue())
  // Sync local state with table data when table data changes
  useEffect(() => {
    setValue(getValue());
  }, [getValue]);

  const onBlur = () => {
    table.options.meta?.updateData(row.index, column.id, value)
  }

  return (
    <input
      tabIndex={-1}
      value={value}
      onChange={e => setValue(e.target.value)}
      onBlur={onBlur}
      type={column.columnDef.meta?.type || "text"}
      disabled={column.columnDef.meta?.readOnly || (DATE_COLUMNS.includes(column.id) && !value)}
      aria-disabled={column.columnDef.meta?.readOnly}
    />
  )
}

const TableTagCell = ({ getValue, row, column, table }) => {
  const [value, setValue] = useState(getValue())

  const onBlur = () => {
    table.options.meta?.updateData(row.index, column.id, value)
  }

  return (
    <TagInput
      trigger={['Enter', 'Comma']}
      size="lg"
      value={value}
      onChange={e => setValue(e)}
      onBlur={onBlur}
      onClean={() => table.options.meta?.updateData(row.index, column.id, [])}
    />
  );
};

const columnHelper = createColumnHelper<OpenAgendaEditoItem>();

const Edito = () => {
  const [tableData, setTableData] = useState<OpenAgendaEditoItem[]>([]);
  const [patchResult, setPatchResult] = useState<any>(null);
  const [isPatching, setIsPatching] = useState(false);


  useEffect(() => {
    const loadEvents = async (): Promise<void> => {
      const response: OpenAgendaEventsReponse = await ky(editoQuery).json();
      const newTableData = response.events.map((event) => {
        const firstTiming = event.timings.length === 1 ? event.timings[0] : null;
        console.log("firstTiming - ", firstTiming);
        return ({
          ...event,
          firstTimingDate: firstTiming?.begin.split("T")[0],
          firstTimingTimeStart: firstTiming?.begin.split("T")[1].slice(0, 5),
          firstTimingTimeEnd: firstTiming?.end.split("T")[1].slice(0, 5),
          hasChanged: false,
        })
      });
      setTableData(newTableData);
    };
    loadEvents();
  }, []);

  const updateData = (rowIndex: number, columnId: keyof OpenAgendaEditoItem, value: string) => {
    setTableData((old) =>
      old.map((row, index) => {
        if (index === rowIndex && row[columnId] !== value) {
          return { ...row, [columnId]: value, hasChanged: true };
        }
        return row;
      })
    );
  };

  const columns = [
    columnHelper.accessor("onlineAccessLink", { header: "ext_link", cell: ExtLinkCell }),
    columnHelper.accessor("slug", { header: "oa_link", cell: OaLinkCell }),
    columnHelper.accessor(row => row.longDescription || row.description, { header: "description" }),
    columnHelper.accessor("dateRange", { header: "date_range" }),
    columnHelper.accessor("firstTimingDate", { header: "date", cell: TableCell }),
    columnHelper.accessor("firstTimingTimeStart", { header: "start", cell: TableCell }),
    columnHelper.accessor("firstTimingTimeEnd", { header: "end", cell: TableCell }),
    columnHelper.accessor("title", { header: "title", cell: TableCell }),
    columnHelper.accessor("keywords", { header: "keywords", cell: TableTagCell }),
    columnHelper.accessor("hasChanged", { header: "has_changed" }),
  ];

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    meta: { updateData },
  });
  console.log("tableData - ", tableData);
  const patchKeywords = async (events: OpenAgendaEditoItem[]) => {
    setIsPatching(true);
    setPatchResult(null);
    const patchedEvents = events
      .filter((event) => event.hasChanged)
      .map((event) => ({ uid: event.uid.toString(), keywords: event.keywords ?? [], slug: event.slug }))
    // Reset hasChanged to false
    setTableData((old) => old.map((event) => ({ ...event, hasChanged: false })));
    // Scroll to top
    window.scrollTo(0, 0);
    try {
      await ky.patch(`${API_URL}/events/keywords`, { json: { events: patchedEvents }, timeout: 20000 }).json();
      setPatchResult(patchedEvents)
    } catch (error) {
      console.error(error);
    }
    setIsPatching(false);
  }

  return (
    <div>
      <div style={{ position: "sticky", top: 0, display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
        <button disabled={isPatching} id="patch" type="button" onClick={() => patchKeywords(tableData)}> Mettre à jour tous les keywords sur OpenAgenda</button>
        {isPatching && <ImSpinner7 id="load-spinner" />}
      </div>
      {tableData && tableData.length > 0 && <pre>{JSON.stringify(tableData
        .filter((e) => e.hasChanged)
        .map((event) => ({ uid: event.uid, keywords: event.keywords ?? [], slug: event.slug })), null, "\t")}</pre>}
      {patchResult?.length > 0 && <pre> Updated events: {`${patchResult.length}\n`} {patchResult.map((e: any) => `${e.slug}: ${e.keywords}`).join("\n")}</pre>}
      <table>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} className={`edito-table-${header.column.id}`}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className={`edito-table-${cell.column.id}`}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
};

export default Edito;
