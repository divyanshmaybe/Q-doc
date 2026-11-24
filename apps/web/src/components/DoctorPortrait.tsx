import doctor from "../assets/consultation-doctor.webp";

export function DoctorPortrait() {
  return (
    <div className="doctor-portrait" aria-hidden="true">
      <img src={doctor} alt="" />
    </div>
  );
}
