import React, { useState, useEffect } from 'react';
import { useTranslation } from './i18n/index.jsx';


function App() {
  const { t, lang, setLang } = useTranslation();
  const [query, setQuery] = useState('');
  const [k, setK] = useState(4);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedArt, setSelectedArt] = useState(null);

  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return saved === 'true';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  const [authorFilter, setAuthorFilter] = useState('');
  const [tipoFilter, setTipoFilter] = useState('');
  const [yearMin, setYearMin] = useState('');
  const [yearMax, setYearMax] = useState('');
  const [titleFilter, setTitleFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [searched, setSearched] = useState(false);

  const hasActiveFilters = authorFilter || tipoFilter || yearMin || yearMax || titleFilter;

  const clearFilters = () => {
    setAuthorFilter('');
    setTipoFilter('');
    setYearMin('');
    setYearMax('');
    setTitleFilter('');
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim() && !hasActiveFilters) return;

    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const params = new URLSearchParams();
      params.append('k', k);
      if (query.trim()) params.append('query', query);
      if (authorFilter) params.append('author', authorFilter);
      if (tipoFilter) params.append('tipo', tipoFilter);
      if (yearMin) params.append('year_min', yearMin);
      if (yearMax) params.append('year_max', yearMax);
      if (titleFilter) params.append('title', titleFilter);

      const response = await fetch(`${apiUrl}/search?${params}`);
      if (!response.ok) throw new Error("Error en la respuesta del servidor");

      const data = await response.json();
      setResults(data);
      setSearched(true);
    } catch (error) {
      console.error("Error en la búsqueda:", error);
      alert(t("error.connection"));
    } finally {
      setLoading(false);
    }
  };

  const activeFilterCount = [authorFilter, tipoFilter, titleFilter].filter(Boolean).length
    + (yearMin ? 1 : 0) + (yearMax ? 1 : 0);

  return (
    <div className="min-w-screen min-h-screen bg-gray-50 dark:bg-gray-900 p-8 font-sans text-gray-800 dark:text-gray-100">
      <div className="max-w-6xl mx-auto">

        {/* Top right: dark mode + language */}
        <div className="flex justify-end gap-2 mb-6">
          <button
            type="button"
            onClick={() => setDarkMode(!darkMode)}
            className="inline-flex items-center justify-center text-base font-medium px-3 py-2 rounded-lg bg-[#1F2937] dark:bg-[#00ADB5] text-white dark:text-[#0F172A] hover:bg-gray-700 dark:hover:bg-[#0095A3] transition-colors"
            title={darkMode ? t("dark.tooltip_light") : t("dark.tooltip_dark")}
          >
            {darkMode ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            )}
          </button>
          <button
            type="button"
            onClick={() => setLang(lang === 'es' ? 'en' : 'es')}
            className="inline-flex items-center justify-center gap-1 text-base font-medium px-3 py-1.5 rounded-lg bg-[#1F2937] dark:bg-[#00ADB5] text-white dark:text-[#0F172A] hover:bg-gray-700 dark:hover:bg-[#0095A3] transition-colors"
            title={t("lang.switch_to")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            {lang === 'es' ? 'EN' : 'ES'}
          </button>
        </div>

        {/* Cabecera y Buscador */}
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">{t("search.title")}</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">{t("search.subtitle")}</p>

          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 justify-center max-w-2xl mx-auto">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("search.placeholder")}
              className="flex-1 p-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 dark:placeholder-gray-500"
            />
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="flex gap-2">
                <input
                  type="number"
                  value={k}
                  onChange={(e) => setK(e.target.value)}
                  min="1"
                  max="20"
                  className="w-20 p-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm text-center bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  title={t("search.results")}
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-[#1F2937] dark:bg-[#00ADB5] text-white dark:text-[#0F172A] hover:bg-gray-700 dark:hover:bg-[#0095A3] text-base font-semibold py-4 px-8 rounded-lg shadow-sm transition-colors disabled:bg-gray-400 dark:disabled:bg-teal-700 flex-1 sm:flex-none"
                >
                  {loading ? t("search.searching") : t("search.button")}
                </button>
              </div>
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="bg-[#1F2937] dark:bg-[#00ADB5] text-white dark:text-[#0F172A] hover:bg-gray-700 dark:hover:bg-[#0095A3] text-base font-semibold px-3 py-4 sm:px-4 rounded-lg shadow-sm transition-colors self-start"
              >
                {t("filters.button")} {activeFilterCount > 0 && `(${activeFilterCount})`}
              </button>
            </div>
          </form>

          {/* Panel de filtros */}
          {showFilters && (
            <div className="mt-4 p-5 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 max-w-2xl mx-auto">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 text-left">{t("filters.title")}</label>
                  <input
                    type="text"
                    value={titleFilter}
                    onChange={(e) => setTitleFilter(e.target.value)}
                    placeholder={t("filters.title_placeholder")}
                    className="w-full p-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 dark:placeholder-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 text-left">{t("filters.artist")}</label>
                  <input
                    type="text"
                    value={authorFilter}
                    onChange={(e) => setAuthorFilter(e.target.value)}
                    placeholder={t("filters.artist_placeholder")}
                    className="w-full p-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 dark:placeholder-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 text-left">{t("filters.type")}</label>
                  <select
                    value={tipoFilter}
                    onChange={(e) => setTipoFilter(e.target.value)}
                    className="w-full p-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="">{t("filters.type_all")}</option>
                    <option value="painting">{t("filters.type_painting")}</option>
                    <option value="drawing">{t("filters.type_drawing")}</option>
                    <option value="photograph">{t("filters.type_photograph")}</option>
                    <option value="photomechanical print">{t("filters.type_photomechanical")}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 text-left">{t("filters.year_min")}</label>
                  <input
                    type="number"
                    value={yearMin}
                    onChange={(e) => setYearMin(e.target.value)}
                    placeholder="Ej: 1500"
                    min="1400"
                    max="2025"
                    className="w-full p-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 dark:placeholder-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 text-left">{t("filters.year_max")}</label>
                  <input
                    type="number"
                    value={yearMax}
                    onChange={(e) => setYearMax(e.target.value)}
                    placeholder="Ej: 1900"
                    min="1400"
                    max="2025"
                    className="w-full p-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 dark:placeholder-gray-500"
                  />
                </div>
              </div>
              {hasActiveFilters && (
                <div className="mt-4 text-center">
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="inline-flex items-center justify-center gap-1 text-sm font-medium px-4 py-2 rounded-lg bg-[#1F2937] dark:bg-[#00ADB5] text-white dark:text-[#0F172A] hover:bg-gray-700 dark:hover:bg-[#0095A3] transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                      <line x1="10" y1="11" x2="10" y2="17"/>
                      <line x1="14" y1="11" x2="14" y2="17"/>
                    </svg>
                    {t("filters.clear")}
                  </button>
                </div>
              )}
            </div>
          )}
        </header>

        {/* Empty state */}
        {searched && results.length === 0 && (
          <div className="text-center py-20">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-gray-300 dark:text-gray-600 mx-auto mb-4">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <p className="text-gray-500 dark:text-gray-400 text-lg">{t("results.empty_title")}</p>
            <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">{t("results.empty_subtitle")}</p>
          </div>
        )}

        {/* Grid de Resultados */}
        <main className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {results.map((art) => (
            <div
              key={art.image_id}
              onClick={() => setSelectedArt(art)}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden cursor-pointer transform transition-transform hover:-translate-y-1 hover:shadow-lg"
            >
              <img
                src={art.image_path}
                alt={art.title}
                className="w-full h-56 object-cover"
                onError={(e) => { e.target.src = "https://via.placeholder.com/400x300?text=Imagen+No+Disponible"; }}
              />
              <div className="p-4">
                <h3 className="font-bold text-lg truncate text-gray-900 dark:text-white" title={art.title}>{art.title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{art.author}</p>
                <div className="mt-2 text-xs text-gray-400 dark:text-gray-500 font-mono text-right">
                  {t("results.score")}: {art.score.toFixed(3)}
                </div>
              </div>
            </div>
          ))}
        </main>

        {/* Modal de Detalles */}
        {selectedArt && (
          <div
            className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedArt(null)}
          >
            <div
              className="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto flex flex-col md:flex-row shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="md:w-1/2 bg-gray-100 dark:bg-gray-700 flex items-center justify-center p-4">
                <img
                  src={selectedArt.image_path}
                  alt={selectedArt.title}
                  className="max-h-full max-w-full object-contain rounded-lg shadow-sm"
                  onError={(e) => { e.target.src = "https://via.placeholder.com/400x300?text=Imagen+No+Disponible"; }}
                />
              </div>
              <div className="p-8 md:w-1/2 flex flex-col">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{selectedArt.title}</h2>
                <p className="text-xl text-gray-600 dark:text-gray-400 italic mb-4">{selectedArt.author}</p>

                <div className="flex flex-wrap gap-3 mb-6">
                  <span className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-sm font-medium px-3 py-1 rounded-full">
                    {t("modal.year")}: {selectedArt.anio || t("modal.unknown")}
                  </span>
                  <span className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 text-sm font-medium px-3 py-1 rounded-full">
                    {t("modal.type")}: {selectedArt.tipo || t("modal.not_specified")}
                  </span>
                </div>

                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">{t("modal.description")}:</h4>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed overflow-y-auto flex-1 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-100 dark:border-gray-700">
                  {selectedArt.description}
                </p>

                <button
                  onClick={() => setSelectedArt(null)}
                  className="mt-6 w-full bg-gray-700 hover:bg-gray-600 dark:bg-gray-500 dark:hover:bg-gray-400 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  {t("modal.close")}
                </button>
              </div>
            </div>
            </div>
          )}
        </div>
      </div>
    );
  }

export default App;