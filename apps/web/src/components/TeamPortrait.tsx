import pig from "../assets/team-pig.webp";
import creeper from "../assets/team-creeper.webp";
import wolf from "../assets/team-wolf.webp";

export const teamPresenters = [
  { name: "Divyansh Soni", portrait: pig },
  { name: "Divyansh Srivastava", portrait: creeper },
  { name: "Sanil", portrait: wolf },
];

export function TeamPortrait({ index }: { index: number }) {
  return (
    <span className={`character-art character-art-${index}`} aria-hidden="true">
      <img className={`story-avatar portrait-${index}`} src={teamPresenters[index].portrait} width="128" height="128" alt="" />
    </span>
  );
}
