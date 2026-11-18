import { AssistantRuntimeProvider, useLocalRuntime } from "@assistant-ui/react";
import { Thread } from "./components/thread.aui";
import axios from "axios";

// FastAPI chat endpoint.
const API_URL = "http://localhost:8000/chat";

// Extracts all text parts from a message and combines them into one string.
const getMessageText = (message) =>
  message.content
    .filter((part) => part.type === "text")
    .map((part) => part.text)
    .join("");

// Connects assistant-ui to the FastAPI backend.
const adapter = {
  // Handles messages sent from the chat interface.
  async run({ messages, abortSignal }) {
    // Gets the latest user message.
    const latestMessage = messages[messages.length - 1];

    // Converts previous messages into conversation history.
    const conversationHistory = messages.slice(0, -1).map((message) => ({
      role: message.role,
      content: getMessageText(message),
    }));

    // Sends the user's message and conversation history to FastAPI.
    const response = await axios.post(
      API_URL,
      {
        message: getMessageText(latestMessage),
        history: conversationHistory,
      },
      {
        signal: abortSignal,
      },
    );

    // Returns the backend response in assistant-ui's expected format.
    return {
      content: [{ type: "text", text: response.data.reply }],
    };
  },
};

const App = () => {
  // Creates the chat runtime using the custom adapter.
  const runtime = useLocalRuntime(adapter);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div dir="rtl" className="h-dvh">
        <Thread />
      </div>
    </AssistantRuntimeProvider>
  );
};

export default App;
