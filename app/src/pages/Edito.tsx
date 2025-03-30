// Init config from codebase
import "./edito.css";
import { editoQuery, OA_SLUG, API_URL } from "../config";
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

// React stuff
import { useEffect, useState } from "react";

const Edito = () => {
	const [isPatching, setIsPatching] = useState(false);

	const patchKeywords = async (events: OpenAgendaEditoItem[]) => {
		setIsPatching(true);
		const patchedEvents = events
			.filter((event) => event.hasChanged)
			.map((event) => ({
				uid: event.uid.toString(),
				keywords: event.keywords ?? [],
				slug: event.slug,
			}));
		// Reset hasChanged to false
		// Scroll to top
		window.scrollTo(0, 0);
		try {
			await ky
				.patch(`${API_URL}/events/keywords`, {
					json: { events: patchedEvents },
					timeout: 20000,
				})
				.json();
		} catch (error) {
			console.error(error);
		}
		setIsPatching(false);
	};

	return (
		<div>
			<div
				style={{
					position: "sticky",
					top: 0,
					display: "flex",
					alignItems: "center",
					justifyContent: "center",
					zIndex: 1000,
				}}
			>
				<button
					disabled={isPatching}
					id="patch"
					type="button"
					onClick={() => console.log("PATCH DATA WIP")}
				>
					{" "}
					Mettre à jour tous les keywords sur OpenAgenda
				</button>
				{isPatching && <ImSpinner7 id="load-spinner" />}
			</div>
		</div>
	);
};

export default Edito;
