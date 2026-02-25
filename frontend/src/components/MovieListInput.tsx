import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, X, ThumbsUp, ThumbsDown, Send } from "lucide-react";

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
  const [likedInput, setLikedInput] = useState("");
  const [dislikedInput, setDislikedInput] = useState("");

  const handleAddLiked = () => {
    if (likedInput.trim()) {
      onAddLiked(likedInput.trim());
      setLikedInput("");
    }
  };

  const handleAddDisliked = () => {
    if (dislikedInput.trim()) {
      onAddDisliked(dislikedInput.trim());
      setDislikedInput("");
    }
  };

  const hasMovies = likedMovies.length > 0 || dislikedMovies.length > 0;

  return (
    <div className="space-y-6">
      {/* Liked Movies */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <ThumbsUp className="h-4 w-4" />
          Movies you liked
        </label>
        <div className="flex gap-2">
          <Input
            placeholder="Enter movie title..."
            value={likedInput}
            onChange={(e) => setLikedInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddLiked()}
            className="bg-background border-border focus:ring-1 focus:ring-foreground"
          />
          <Button variant="outline" size="icon" onClick={handleAddLiked}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
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
        <div className="flex gap-2">
          <Input
            placeholder="Enter movie title..."
            value={dislikedInput}
            onChange={(e) => setDislikedInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddDisliked()}
            className="bg-background border-border focus:ring-1 focus:ring-foreground"
          />
          <Button variant="outline" size="icon" onClick={handleAddDisliked}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
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
