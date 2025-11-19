"use client";

import { useState } from "react";
import { RagRequest } from "../definitions";

export type NewsRagProp = {
  ticker: string;
};

export type RagResponse = {
  ticker: string;
  llm_response: Messages;
};

export type Messages = {
  messages: Message[];
};

export type Message = {
  content: string;
  type: "human" | "ai" | string;
  name: string | null;
};

export default function StockRagChatUI({ ticker }: NewsRagProp) {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>(
    []
  );
  const [query, setQuery] = useState("");

  async function handleRag() {
    const user_query = query;
    setQuery("");
    // const user_question=messages[-1]
    const rag_response = await fetch(`http://localhost:8000/ticker/rag`, {
      headers: { "Content-Type": "application/json" },
      method: "POST",
      body: JSON.stringify({
        ticker: ticker,
        source: "news",
        query: user_query,
      }),
    });

    if (!rag_response.ok) {
      return;
    }

    const data: RagResponse = await rag_response.json();
    console.log(data);
    const ai_response = {
      sender: "ai",
      text: data.llm_response.messages[1].content,
    };
    setMessages([
      ...messages,
      { sender: "user", text: user_query },
      ai_response,
    ]);
  }
  return (
    <div className="bg-white rounded-xl shadow-lg p-4 h-[85vh] flex flex-col border border-gray-200">
      {/* Header */}
      <h2 className="text-xl font-bold text-gray-800 mb-3">
        AI Stock Assistant
      </h2>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-3 space-y-3">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-10">
            Ask me about the stock, its news, or fundamentals.
          </p>
        )}

        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex ${
              m.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`px-3 py-2 rounded-lg max-w-[80%] text-sm ${
                m.sender === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-900"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500"
          placeholder="Ask a question..."
          onChange={(e) => setQuery(e.target.value)}
          value={query}
        />

        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700"
          onClick={handleRag}
        >
          Send
        </button>
      </div>
    </div>
  );
}
