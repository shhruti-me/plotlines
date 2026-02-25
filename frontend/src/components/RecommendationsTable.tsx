import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export interface MovieRecommendation {
  id: number;
  title: string;
  score: number;
  year?: number;
  genres?: string;
}

interface RecommendationsTableProps {
  recommendations: MovieRecommendation[];
  isLoading?: boolean;
}

const RecommendationsTable = ({ recommendations, isLoading }: RecommendationsTableProps) => {
  if (isLoading) {
    return (
      <div className="border border-border">
        <div className="p-8 text-center text-muted-foreground">
          Loading recommendations...
        </div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="border border-border">
        <div className="p-8 text-center text-muted-foreground">
          No recommendations yet. Enter your preferences above.
        </div>
      </div>
    );
  }

  return (
    <div className="border border-border">
      <Table>
        <TableHeader>
          <TableRow className="border-b border-border hover:bg-transparent">
            <TableHead className="text-xs uppercase tracking-wider font-medium text-muted-foreground">#</TableHead>
            <TableHead className="text-xs uppercase tracking-wider font-medium text-muted-foreground">Title</TableHead>
            <TableHead className="text-xs uppercase tracking-wider font-medium text-muted-foreground">Year</TableHead>
            <TableHead className="text-xs uppercase tracking-wider font-medium text-muted-foreground">Genres</TableHead>
            <TableHead className="text-xs uppercase tracking-wider font-medium text-muted-foreground text-right">Score</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {recommendations.map((movie, index) => (
            <TableRow key={movie.id} className="border-b border-border">
              <TableCell className="font-mono text-muted-foreground">{index + 1}</TableCell>
              <TableCell className="font-medium">{movie.title}</TableCell>
              <TableCell className="text-muted-foreground">{movie.year || "—"}</TableCell>
              <TableCell className="text-muted-foreground">{movie.genres || "—"}</TableCell>
              <TableCell className="text-right font-mono">{movie.score.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default RecommendationsTable;
