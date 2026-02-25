import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

interface TextPreferenceInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

const TextPreferenceInput = ({ value, onChange, onSubmit }: TextPreferenceInputProps) => {
  return (
    <div className="space-y-4">
      <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
        Describe your preferences
      </label>
      <Textarea
        placeholder="e.g., I love Jamie Campbell Bower as an actor and I enjoy romance and thriller genres..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[120px] resize-none bg-background border-border focus:ring-1 focus:ring-foreground"
      />
      <Button onClick={onSubmit} className="w-full" disabled={!value.trim()}>
        <Send className="mr-2 h-4 w-4" />
        Get Recommendations
      </Button>
    </div>
  );
};

export default TextPreferenceInput;
