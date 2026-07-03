import { Button } from "@/components/ui/button";
import { X, ThumbsUp, ThumbsDown, Send } from "lucide-react";
import MovieAutocomplete from "@/components/MovieAutocomplete";

interface MovieListInputProps {
  likedMovies: string[];
  dislikedMovies: string[];
  onAddLiked: (movie: string) => void;
  onRemoveLiked: (movie: string) => void;
  onAddDisliked: (movie: string) => void;
  onRemoveDisliked: (movie: string) => void;
  onSubmit: () => void;
}

const MovieListInput = ({
  likedMovies,
  dislikedMovies,
  onAddLiked,
  onRemoveLiked,
  onAddDisliked,
  onRemoveDisliked,
  onSubmit,
}: MovieListInputProps) => {
  const hasMovies = likedMovies.length > 0 || dislikedMovies.length > 0;

  return (
    <div className="space-y-6">
      {/* Liked Movies */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <ThumbsUp className="h-4 w-4" />
          Movies you liked
        </label>
        <MovieAutocomplete placeholder="Search liked movie..." onSelect={onAddLiked} />
        <div className="flex flex-wrap gap-2">
          {likedMovies.map((movie) => (
            <span
              key={movie}
              className="inline-flex items-center gap-1 px-3 py-1 text-sm bg-secondary text-secondary-foreground border border-border"
            >
              {movie}
              <button onClick={() => onRemoveLiked(movie)} className="hover:text-destructive">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Disliked Movies */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <ThumbsDown className="h-4 w-4" />
          Movies you disliked
        </label>
        <MovieAutocomplete placeholder="Search disliked movie..." onSelect={onAddDisliked} />
        <div className="flex flex-wrap gap-2">
          {dislikedMovies.map((movie) => (
            <span
              key={movie}
              className="inline-flex items-center gap-1 px-3 py-1 text-sm bg-secondary text-secondary-foreground border border-border"
            >
              {movie}
              <button onClick={() => onRemoveDisliked(movie)} className="hover:text-destructive">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      </div>

      <Button onClick={onSubmit} className="w-full" disabled={!hasMovies}>
        <Send className="mr-2 h-4 w-4" />
        Get Recommendations
      </Button>
    </div>
  );
};

export default MovieListInput;