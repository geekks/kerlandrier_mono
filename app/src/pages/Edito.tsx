// Config related to OpenAgenda & API
import { editoQuery, OA_SLUG, API_URL } from "../config";
import "../frugal.css";

// Import OpenAgenda types
import type {
	OpenAgendaEditoItem,
	OpenAgendaEditoResponse,
	OpenAgendaEventsReponse,
} from "../types/OpenAgenda";

// HTTP & query libs
import ky from "ky";
import { useQuery } from "@tanstack/react-query";
import { ImSpinner7 } from "react-icons/im";

const Edito = () => {
	return (
		<div>
			<div className="flex items-center justify-center sticky top-0 z-[1000]">
				<button
					className="block cursor-pointer
           my-1 p-10 
           text-xl font-barlow uppercase text-teal bg-[#FFFFF0]

           "
					type="button"
					onClick={() => console.log("PATCH DATA WIP")}
				>
					Charger les prochains événements pour EDITO-KEYWORDS
				</button>
			</div>
			<div className="h-[2000px]">A</div>
		</div>
	);
};

export default Edito;
