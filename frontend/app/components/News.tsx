import { useEffect, useState } from "react";
import { NewsParagraph, NewsResponse } from "../definitions";

type NewsRequestResponse = {
  ticker: string;
  news: NewsResponse[];
};

export default function NewsPage({ ticker }: { ticker: string }) {
  const [news, setNews] = useState<NewsResponse[] | null>(null);
  const [expandedArticles, setExpandedArticles] = useState<Set<string>>(
    new Set()
  );

  useEffect(() => {
    async function loadData() {
      const resp = await fetch(
        `http://localhost:8000/ticker/get-ticker-news?ticker=${ticker}`
      );
      const data: NewsRequestResponse = await resp.json();
      setNews(data.news);
    }
    loadData();
  }, [ticker]);

  const toggleArticle = (uuid: string) => {
    setExpandedArticles((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(uuid)) {
        newSet.delete(uuid);
      } else {
        newSet.add(uuid);
      }
      return newSet;
    });
  };

  if (!news)
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-blue-900 mb-6">Latest News</h1>
        <div className="text-center py-8">
          <p className="text-gray-600">Loading news...</p>
        </div>
      </div>
    );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-blue-900 mb-6">Latest News</h1>

      <div className="space-y-4">
        {news.map((n) => {
          const isExpanded = expandedArticles.has(n.uuid);
          const firstParagraph = n.news[0];

          return (
            <div
              className="bg-white rounded-xl border border-blue-100 p-5 hover:border-blue-200 transition-colors"
              key={n.uuid}
            >
              {/* Article Header */}
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-blue-800 mb-1 line-clamp-2">
                    {n.title}
                  </h2>
                  <p className="text-sm text-blue-600 mb-2">{n.publisher}</p>
                </div>
                <a
                  href={n.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-4 px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors whitespace-nowrap"
                >
                  Full Article
                </a>
              </div>

              {/* Article Content */}
              {firstParagraph && (
                <div className="mb-3">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">
                    {firstParagraph.highlight}
                  </h3>
                  <p className="text-gray-800 text-sm leading-relaxed">
                    {isExpanded
                      ? firstParagraph.paragraph
                      : `${firstParagraph.paragraph.slice(0, 150)}...`}
                  </p>
                </div>
              )}

              {/* Additional Paragraphs (when expanded) */}
              {isExpanded &&
                n.news.slice(1).map((paragraph) => (
                  <div key={paragraph.paragraph_number} className="mb-3">
                    <h3 className="text-sm font-medium text-gray-700 mb-1">
                      {paragraph.highlight}
                    </h3>
                    <p className="text-gray-800 text-sm leading-relaxed">
                      {paragraph.paragraph}
                    </p>
                  </div>
                ))}

              {/* Expand/Collapse Button */}
              {firstParagraph && firstParagraph.paragraph.length > 150 && (
                <button
                  onClick={() => toggleArticle(n.uuid)}
                  className="text-blue-600 text-sm font-medium hover:text-blue-800 transition-colors"
                >
                  {isExpanded ? "Show Less" : "Read More"}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {news.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-600">No news available for this stock.</p>
        </div>
      )}
    </div>
  );
}
