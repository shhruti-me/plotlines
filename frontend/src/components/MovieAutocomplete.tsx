import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";

interface MovieSuggestion {
  id: number;
  title: string;
  poster: string | null;
}

interface MovieAutocompleteProps {
  placeholder?: string;
  onSelect: (movieTitle: string) => void;
}

const MovieAutocomplete = ({ placeholder = "Search movie...", onSelect }: MovieAutocompleteProps) => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<MovieSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const res = await fetch(`http://127.0.0.1:8000/search?q=${encodeURIComponent(query)}`);        const data: MovieSuggestion[] = await res.json();
        setSuggestions(data);
        setIsOpen(data.length > 0);
      } catch {
        setSuggestions([]);
        setIsOpen(false);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (title: string) => {
    onSelect(title);
    setQuery("");
    setSuggestions([]);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className="relative flex-1">
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="bg-background border-border focus:ring-1 focus:ring-foreground"
      />
      {isOpen && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 border border-border bg-popover text-popover-foreground max-h-[300px] overflow-y-auto animate-in fade-in-0 zoom-in-95 duration-150">
          {suggestions.map((movie) => (
            <button
              key={movie.id}
              onClick={() => handleSelect(movie.title)}
              className="flex items-center gap-3 w-full px-3 py-2 text-left hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              {movie.poster ? (
                <img
                  src={movie.poster}
                  alt={movie.title}
                  className="w-[50px] h-[75px] object-cover flex-shrink-0 bg-muted"
                />
              ) : (
                <div className="w-[50px] h-[75px] bg-muted flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-muted-foreground">N/A</span>
                </div>
              )}
              <span className="text-sm truncate">{movie.title}</span>
            </button>
          ))}
        </div>
      )}
      {isLoading && query.length >= 2 && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 border border-border bg-popover p-3 text-center text-sm text-muted-foreground">
          Searching...
        </div>
      )}
    </div>
  );
};

export default MovieAutocomplete;