
import argparse
import json
import time
from datetime import datetime
from math import ceil

import requests

API_URL = "https://www.crtm.es/widgets/api/GetStopsTimes.php"

# Paradas candidatas de UPM Montegancedo y Montepríncipe.
# 08771 ya ha sido probada con éxito.
# Las demás deben comprobarse con el servicio CRTM.
STOPS = {
    "UPM - M Informática": ["17572", "17573"],
    "UPM - Servicios Centrales": ["17574", "17575"],
    "UPM - USOC Aeronáutica": ["17566", "17567"],
    "UPM - Badajoz ETSIINF": ["08411"],
    "UPM - Avenida Montepríncipe": ["08771", "08758"],
}


def parse_datetime(value):
    if not value:
        return None

    return datetime.fromisoformat(
        str(value).replace("Z", "+00:00")
    )


def get_arrivals(stop_id):
    """Obtiene las próximas llegadas de una parada CRTM."""

    stop_id = str(stop_id).strip()

    response = requests.get(
        API_URL,
        params={
            "codStop": f"8_{stop_id}",
            "type": 0,
            "orderBy": 2,
            "stopTimesByIti": "",
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("error"):
        raise RuntimeError(
            data.get("message", "Error de CRTM")
        )

    info = data.get("stopTimes")

    if not isinstance(info, dict):
        raise RuntimeError("Respuesta CRTM inesperada")

    server_now = parse_datetime(info.get("actualDate"))

    if server_now is None:
        server_now = datetime.now().astimezone()

    raw = (info.get("times") or {}).get("Time", [])

    if isinstance(raw, dict):
        raw = [raw]

    arrivals = []

    for bus in raw or []:
        arrival_time = parse_datetime(bus.get("time"))

        minutes = None

        if arrival_time is not None:
            seconds = (
                arrival_time - server_now
            ).total_seconds()

            minutes = max(0, ceil(seconds / 60))

        line_info = bus.get("line") or {}
        destination_stop = bus.get("destinationStop") or {}

        arrivals.append({
            "line": line_info.get("shortDescription", "?"),
            "destination": (
                destination_stop.get("name")
                or bus.get("destination")
                or "Desconocido"
            ),
            "direction": bus.get("direction"),
            "arrival_time": (
                arrival_time.strftime("%H:%M:%S")
                if arrival_time
                else None
            ),
            "minutes": minutes,
            "issue_id": bus.get("codIssue"),
        })

    arrivals.sort(
        key=lambda bus: (
            bus["minutes"] is None,
            bus["minutes"]
            if bus["minutes"] is not None
            else float("inf"),
        )
    )

    stop_info = info.get("stop") or {}

    return {
        "stop_id": stop_id,
        "stop_name": stop_info.get("name", ""),
        "updated_at": info.get("actualDate"),
        "arrivals": arrivals,
    }


def print_stop(stop_id):
    print(f"\n{'-' * 70}")
    print(f"PARADA {stop_id}")
    print("-" * 70)

    try:
        result = get_arrivals(stop_id)

        if result["stop_name"]:
            print("Nombre:", result["stop_name"])

        print("Actualizado:", result["updated_at"])

        if not result["arrivals"]:
            print("No hay próximas llegadas disponibles.")
            return

        print(
            f"\n{'LÍNEA':<8}"
            f"{'DESTINO':<35}"
            f"{'HORA':<12}"
            f"{'ESPERA'}"
        )

        for bus in result["arrivals"]:
            eta = (
                f"{bus['minutes']} min"
                if bus["minutes"] is not None
                else "N/D"
            )

            print(
                f"{str(bus['line']):<8}"
                f"{str(bus['destination'])[:34]:<35}"
                f"{str(bus['arrival_time']):<12}"
                f"{eta}"
            )

    except (requests.RequestException,
            RuntimeError, ValueError) as error:
        print("Error:", error)


def print_all():
    print("\n" + "=" * 70)
    print("UPM MONTEGANCEDO / MONTEPRÍNCIPE")
    print("PRÓXIMAS LLEGADAS CRTM")
    print("=" * 70)

    for name, stop_ids in STOPS.items():
        print(f"\n### {name}")

        for stop_id in stop_ids:
            print_stop(stop_id)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--stop",
        help="Consultar una parada específica",
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Actualizar cada 30 segundos",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Mostrar los resultados en JSON",
    )

    args = parser.parse_args()

    while True:
        if args.json:
            if args.stop:
                result = get_arrivals(args.stop)
            else:
                result = {}

                for name, stop_ids in STOPS.items():
                    result[name] = {}

                    for stop_id in stop_ids:
                        try:
                            result[name][stop_id] = get_arrivals(
                                stop_id
                            )
                        except Exception as error:
                            result[name][stop_id] = {
                                "error": str(error)
                            }

            print(json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ))

        elif args.stop:
            print_stop(args.stop)

        else:
            print_all()

        if not args.watch:
            break

        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nPrograma finalizado.")
            break


if __name__ == "__main__":
    main()
