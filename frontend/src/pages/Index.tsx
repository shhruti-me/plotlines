import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import TextPreferenceInput from "@/components/TextPreferenceInput";
import MovieListInput from "@/components/MovieListInput";
import RecommendationsTable, {
  MovieRecommendation,
} from "@/components/RecommendationsTable";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { MessageSquare, List, User, Check, Loader2 } from "lucide-react";

import {
  verifyUser,
  submitTextPreferences,
  submitMovieLists,
} from "@/lib/api";

const Index = () => {
  const [username, setUsername] = useState("");
  const [isUsernameVerified, setIsUsernameVerified] = useState(false);
  const [isCheckingUsername, setIsCheckingUsername] = useState(false);

  const [textPreference, setTextPreference] = useState("");
  const [likedMovies, setLikedMovies] = useState<string[]>([]);
  const [dislikedMovies, setDislikedMovies] = useState<string[]>([]);

  const [recommendations, setRecommendations] =
    useState<MovieRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // ✅ Username verification
  const handleUsernameCheck = async () => {

  if (!username.trim()) return;

  setIsCheckingUsername(true);

  try {
    const res = await verifyUser(username);
    console.log("verifyUser response:", res);

    if (res?.verified) {
      setIsUsernameVerified(true);
    } else {
      alert("Username verification failed");
    }
  } catch (err) {
    console.error("Username verification failed", err);
    alert("Backend not reachable or error occurred");
  } finally {
    setIsCheckingUsername(false);
  }
  console.log("Continue clicked");

};


  // ✅ Text preference submit
  const handleTextSubmit = async () => {
    if (!textPreference.trim()) return;

    setIsLoading(true);
    try {
      const res = await submitTextPreferences(username, textPreference);
      setRecommendations(
        res.recommendations.map(
          ([title, score]: [string, number], i: number) => ({
            id: i,
            title,
            score,
          })
        )
      );
    } catch (err) {
      console.error("Text preference failed", err);
    } finally {
      setIsLoading(false);
    }
  };

  // ✅ Movie list submit
  const handleMovieListSubmit = async () => {
    if (likedMovies.length === 0 && dislikedMovies.length === 0) return;

    setIsLoading(true);
    try {
      const res = await submitMovieLists(
        username,
        likedMovies,
        dislikedMovies
      );
      setRecommendations(
        res.recommendations.map(
          ([title, score]: [string, number], i: number) => ({
            id: i,
            title,
            score,
          })
        )
      );
    } catch (err) {
      console.error("Movie list submit failed", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-3xl py-12 px-4">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-3xl font-medium tracking-tight mb-2">
            Movie Recommender
          </h1>
          <p className="text-muted-foreground">
            Get personalized movie recommendations
          </p>
        </header>

        {/* Username Section */}
        <section className="mb-8">
          <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
            Username
          </label>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setIsUsernameVerified(false);
                }}
                placeholder="Enter your username"
                className="pl-10"
                disabled={isUsernameVerified}
              />
            </div>
            <Button
              type="button"
              onClick={handleUsernameCheck}
              disabled={
                !username.trim() ||
                isCheckingUsername ||
                isUsernameVerified
              }
              variant={isUsernameVerified ? "secondary" : "default"}
            >
              {isCheckingUsername ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : isUsernameVerified ? (
                <>
                  <Check className="h-4 w-4 mr-1" />
                  Verified
                </>
              ) : (
                "Continue"
              )}
            </Button>
          </div>
        </section>

        {/* Inputs */}
        {isUsernameVerified && (
          <section className="mb-12">
            <Tabs defaultValue="text" className="w-full">
              <TabsList className="w-full mb-6 bg-secondary border border-border">
                <TabsTrigger value="text" className="flex-1 gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Text Input
                </TabsTrigger>
                <TabsTrigger value="movies" className="flex-1 gap-2">
                  <List className="h-4 w-4" />
                  Movie Lists
                </TabsTrigger>
              </TabsList>

              <TabsContent value="text">
                <TextPreferenceInput
                  value={textPreference}
                  onChange={setTextPreference}
                  onSubmit={handleTextSubmit}
                />
              </TabsContent>

              <TabsContent value="movies">
                <MovieListInput
                  likedMovies={likedMovies}
                  dislikedMovies={dislikedMovies}
                  onAddLiked={(m) =>
                    setLikedMovies((prev) => [...prev, m])
                  }
                  onRemoveLiked={(m) =>
                    setLikedMovies((prev) =>
                      prev.filter((x) => x !== m)
                    )
                  }
                  onAddDisliked={(m) =>
                    setDislikedMovies((prev) => [...prev, m])
                  }
                  onRemoveDisliked={(m) =>
                    setDislikedMovies((prev) =>
                      prev.filter((x) => x !== m)
                    )
                  }
                  onSubmit={handleMovieListSubmit}
                />
              </TabsContent>
            </Tabs>
          </section>
        )}

        {/* Results */}
        {isUsernameVerified && (
          <section>
            <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
              Recommendations
            </h2>
            <RecommendationsTable
              recommendations={recommendations}
              isLoading={isLoading}
            />
          </section>
        )}
      </div>
    </div>
  );
};

export default Index;
