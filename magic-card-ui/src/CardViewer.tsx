import { useEffect, useState } from "react";

const COLOR_MAP = {
    white: ["w", "white"],
    blue: ["u", "blue"],
    black: ["b", "black"],
    red: ["r", "red"],
    green: ["g", "green"],
    colorless: ["c", "colorless"]
};

export default function CardViewer() {
    const [cards, setCards] = useState([]);
    const [hoveredCard, setHoveredCard] = useState(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const [search, setSearch] = useState("");

    useEffect(() => {
        fetch("/resources/card_tags_merged.json")
            .then(res => res.json())
            .then(data => setCards(Object.values(data)));
    }, []);

    const matchesColor = (colors: string | string[], searchTerm: string) => {
        if (!colors || !searchTerm) return false;
        const lower = searchTerm.toLowerCase();
        return Object.entries(COLOR_MAP).some(([color, aliases]) => {
            return aliases.includes(lower) && colors.includes(color.charAt(0).toUpperCase());
        });
    };

    const matchesTerm = (card: { name: string; tags: any[]; auto_tags: any[]; text_tags: any[]; colors: string | string[]; }, term: string) => {
        return (
            card.name.toLowerCase().includes(term) ||
            card.tags?.some(tag => tag.includes(term)) ||
            card.auto_tags?.some(tag => tag.includes(term)) ||
            card.text_tags?.some(tag => tag.includes(term)) ||
            matchesColor(card.colors, term)
        );
    };

    const filtered = cards.filter(card => {
        const terms = search.toLowerCase().split(" ").filter(Boolean);
        return terms.every(term => matchesTerm(card, term));
    });

    const renderTagGroup = (title: string, tags: any[], color: { bg: any; text: any; }) => (
        tags?.length > 0 && (
            <div className="mb-1">
                <p className="text-[10px] font-medium text-gray-300 mb-0.5">{title}</p>
                <div className="flex flex-wrap gap-1">
                    {tags.sort().map((tag, j) => (
                        <span
                            key={title + j}
                            className={`text-[10px] ${color.bg} ${color.text} px-1 py-[2px] rounded`}
                            title={title}
                        >
              {tag}
            </span>
                    ))}
                </div>
            </div>
        )
    );

    return (
        <div
            className="p-4 bg-gray-900 min-h-screen text-white"
            onMouseMove={(e) => setMousePos({ x: e.clientX, y: e.clientY })}
        >
            <div className="sticky top-0 z-40 mb-4 bg-gray-800 bg-opacity-95 backdrop-blur-sm rounded-xl shadow-lg p-3 flex items-center justify-between gap-2">
                <input
                    placeholder="🔍 Suche nach Kreaturen, Farben (wie 'blue', 'white', etc.) oder Tags..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-indigo-500 bg-gray-700 text-white placeholder:text-indigo-300 shadow-inner focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all duration-200"
                />
            </div>

            <div className="relative grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {filtered.map((card, i) => (
                    <div
                        key={i}
                        className="group relative border border-gray-700 rounded-xl shadow bg-gray-800 overflow-hidden"
                        onMouseEnter={() => setHoveredCard(card)}
                        onMouseLeave={() => setHoveredCard(null)}
                    >
                        <div className="w-full aspect-[3/4] bg-gray-700 relative">
                            <img
                                src={card.image_url}
                                alt={card.name}
                                className="w-full h-full object-cover transition-transform duration-300"
                            />
                        </div>
                        <div className="p-2">
                            <h2 className="text-sm font-semibold mb-1 truncate text-indigo-200">{card.name}</h2>
                            <p className="text-xs italic mb-1 text-gray-300 line-clamp-2">{card.caption}</p>
                            {renderTagGroup("Vision Model", card.tags, { bg: "bg-blue-800", text: "text-blue-100" })}
                            {renderTagGroup("Caption/NLP", card.auto_tags, { bg: "bg-green-800", text: "text-green-100" })}
                            {renderTagGroup("Textanalyse (type_line, flavor_text)", card.text_tags, { bg: "bg-purple-800", text: "text-purple-100" })}
                        </div>
                    </div>
                ))}
            </div>

            {hoveredCard && (
                <div
                    className="fixed z-50 p-2 bg-white shadow-2xl rounded-xl border transition-opacity duration-300"
                    style={{
                        top: mousePos.y + 20,
                        left: mousePos.x + 20,
                        opacity: hoveredCard ? 1 : 0
                    }}
                >
                    <img
                        src={hoveredCard.image_url}
                        alt={hoveredCard.name}
                        className="w-72 h-auto object-cover rounded"
                    />
                </div>
            )}
        </div>
    );
}
