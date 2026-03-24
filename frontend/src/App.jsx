import React, { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [k, setK] = useState(5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedArt, setSelectedArt] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      // Conexión con el backend
      const response = await fetch(`http://localhost:8000/search?query=${encodeURIComponent(query)}&k=${k}`);
      if (!response.ok) throw new Error("Error en la respuesta del servidor");
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Error en la búsqueda:", error);
      alert("No se pudo conectar con la API. Asegúrate de que FastAPI está corriendo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-w-screen min-h-screen bg-gray-50 p-8 font-sans text-gray-800">
      <div className="max-w-6xl mx-auto">
        
        {/* Cabecera y Buscador */}
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold mb-4 text-gray-900">Buscador Semántico de Arte</h1>
          <p className="text-gray-600 mb-8">Describe la atmósfera, los colores o los elementos de la obra que buscas.</p>
          
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 justify-center max-w-2xl mx-auto">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ej: Un paisaje sombrío con pinceladas marcadas..."
              className="flex-1 p-4 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <div className="flex gap-2">
              <input 
                type="number" 
                value={k}
                onChange={(e) => setK(e.target.value)}
                min="1"
                max="20"
                className="w-20 p-4 border border-gray-300 rounded-lg shadow-sm text-center"
                title="Número de resultados (K)"
              />
              <button 
                type="submit" 
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-lg shadow-sm transition-colors disabled:bg-blue-400"
              >
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
            </div>
          </form>
        </header>

        {/* Grid de Resultados */}
        <main className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {results.map((art) => (
            <div 
              key={art.image_id} 
              onClick={() => setSelectedArt(art)}
              className="bg-white rounded-xl shadow-md overflow-hidden cursor-pointer transform transition-transform hover:-translate-y-1 hover:shadow-lg"
            >
              {/* FastAPI sirve las imágenes estáticamente */}
              <img 
                src={`http://localhost:8000/images/${art.image_id}.jpg`} 
                alt={art.title} 
                className="w-full h-56 object-cover"
                onError={(e) => { e.target.src = "https://via.placeholder.com/400x300?text=Imagen+No+Disponible"; }}
              />
              <div className="p-4">
                <h3 className="font-bold text-lg truncate" title={art.title}>{art.title}</h3>
                <p className="text-sm text-gray-500 truncate">{art.author}</p>
                <div className="mt-2 text-xs text-gray-400 font-mono text-right">
                  Score: {art.score.toFixed(3)}
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
              className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto flex flex-col md:flex-row shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="md:w-1/2 bg-gray-100 flex items-center justify-center p-4">
                <img 
                  src={`http://localhost:8000/images/${selectedArt.image_id}.jpg`} 
                  alt={selectedArt.title} 
                  className="max-h-full max-w-full object-contain rounded-lg shadow-sm"
                  onError={(e) => { e.target.src = "https://via.placeholder.com/600x600?text=Imagen+No+Disponible"; }}
                />
              </div>
              <div className="p-8 md:w-1/2 flex flex-col">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">{selectedArt.title}</h2>
                <p className="text-xl text-gray-600 italic mb-4">{selectedArt.author}</p>
                
                <div className="flex flex-wrap gap-3 mb-6">
                  <span className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                    Año: {selectedArt.anio || 'Desconocido'}
                  </span>
                  <span className="bg-purple-100 text-purple-800 text-sm font-medium px-3 py-1 rounded-full">
                    Tipo: {selectedArt.tipo || 'No especificado'}
                  </span>
                </div>
                
                <h4 className="font-semibold text-gray-900 mb-2">Descripción del análisis:</h4>
                <p className="text-gray-700 leading-relaxed overflow-y-auto flex-1 bg-gray-50 p-4 rounded-lg border border-gray-100">
                  {selectedArt.description}
                </p>
                
                <button 
                  onClick={() => setSelectedArt(null)}
                  className="mt-6 w-full bg-gray-900 hover:bg-gray-800 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Cerrar Detalles
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