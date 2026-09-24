from .database import init_db, get_connection, add_vehicle

SAMPLE_VEHICLES = [
    {
        "plate_number": "GA07AB1234",
        "vehicle_type": "motorcycle",
        "color": "black",
        "make": "Honda",
        "model": "Activa",
        "registration_status": "Active"
    },
    {
        "plate_number": "MH12DE1433",
        "vehicle_type": "car",
        "color": "white",
        "make": "Hyundai",
        "model": "i20",
        "registration_status": "Active"
    },
    {
        "plate_number": "DL01CA9999",
        "vehicle_type": "car",
        "color": "red",
        "make": "Maruti",
        "model": "Swift",
        "registration_status": "Active"
    },
    {
        "plate_number": "KA03XY5678",
        "vehicle_type": "truck",
        "color": "blue",
        "make": "Tata",
        "model": "Ace",
        "registration_status": "Suspended"
    },
    {
        "plate_number": "HR26DQ5555",
        "vehicle_type": "car",
        "color": "silver_grey",
        "make": "Honda",
        "model": "City",
        "registration_status": "Active"
    }
]

def seed_demo_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if vehicles already exist
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        print("[AVNIT] Seeding initial demo registration records...")
        for v in SAMPLE_VEHICLES:
            add_vehicle(
                plate_number=v["plate_number"],
                vehicle_type=v["vehicle_type"],
                color=v["color"],
                make=v["make"],
                model=v["model"],
                registration_status=v["registration_status"]
            )
        print(f"[AVNIT] Successfully seeded {len(SAMPLE_VEHICLES)} demo vehicles.")
    else:
        print(f"[AVNIT] Database already contains {count} registered vehicles.")

if __name__ == "__main__":
    seed_demo_database()
