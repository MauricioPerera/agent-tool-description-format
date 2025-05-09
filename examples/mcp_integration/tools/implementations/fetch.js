/**
 * Implementación de la herramienta fetch para la integración ATDF-MCP.
 * 
 * Esta implementación demuestra cómo crear la lógica de ejecución para una
 * herramienta definida en formato ATDF. La herramienta simula una petición
 * HTTP para recuperar contenido web.
 * 
 * En un entorno de producción, esta implementación utilizaría fetch, axios
 * u otra biblioteca para realizar peticiones HTTP reales.
 * 
 * Corresponde a la definición en ../fetch.json
 */

/**
 * Función principal que implementa la herramienta fetch.
 * 
 * @param {Object} params - Parámetros validados por el adaptador ATDF-MCP
 * @param {string} params.url - URL a la que realizar la petición
 * @param {boolean} [params.raw=false] - Si es true, devuelve HTML crudo
 * @returns {Promise<Object>} Resultado de la petición
 * @throws {Error} Error con código 'invalid_url' si la URL es inválida
 * @throws {Error} Error con código 'fetch_error' si ocurre un error en la petición
 */
module.exports = async function fetchImplementation(params) {
  const { url, raw = false } = params;
  
  // Validación básica de URL
  if (!url || !url.startsWith('http')) {
    throw new Error('invalid_url');
  }
  
  try {
    console.log(`Simulando petición a: ${url} (raw: ${raw})`);
    
    // Simular un pequeño retraso para imitar la latencia de red
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Construir respuesta simulada según el parámetro 'raw'
    if (raw) {
      // Devolver HTML simulado cuando se solicita contenido crudo
      return {
        status: 200,
        content: `
          <!DOCTYPE html>
          <html>
            <head>
              <title>Página simulada - ${url}</title>
            </head>
            <body>
              <h1>Contenido simulado para ${url}</h1>
              <p>Esta es una respuesta simulada para demostrar la herramienta fetch.</p>
              <ul>
                <li>Elemento 1</li>
                <li>Elemento 2</li>
                <li>Elemento 3</li>
              </ul>
            </body>
          </html>
        `
      };
    } else {
      // Devolver contenido procesado y estructurado
      return {
        status: 200,
        url: url,
        title: `Página simulada - ${url}`,
        content: {
          headings: ["Contenido simulado para " + url],
          paragraphs: ["Esta es una respuesta simulada para demostrar la herramienta fetch."],
          links: [
            { text: "Link 1", url: "https://example.com/1" },
            { text: "Link 2", url: "https://example.com/2" }
          ]
        },
        metadata: {
          fetchedAt: new Date().toISOString(),
          contentType: "text/html"
        }
      };
    }
  } catch (error) {
    console.error(`Error al recuperar ${url}:`, error);
    throw new Error('fetch_error');
  }
}; 