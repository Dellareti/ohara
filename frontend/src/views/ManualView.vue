<template>
  <div class="manual-container">
    <div class="manual-header">
      <h1>Manual de Uso - Ohara</h1>
      <p>Guia completo para usar o seu leitor de mangá</p>
    </div>

    <div class="manual-content">
      <section id="getting-started" class="manual-section">
        <h2>Primeiros Passos</h2>
        <div class="content-grid">
          <div class="info-card">
            <h3>1. Configuração Inicial</h3>
            <p>Acesse <strong>Configurações</strong> no menu principal para definir suas preferências de leitura e interface.</p>
          </div>
          <div class="info-card">
            <h3>2. Adicionar Mangás</h3>
            <p>Use a função de <strong>Setup</strong> para adicionar seus mangás ao sistema.</p>
          </div>
          <div class="info-card">
            <h3>3. Organização</h3>
            <p>Organize sua biblioteca usando filtros, ordenação e diferentes visualizações de cards.</p>
          </div>
        </div>
      </section>

      <section id="library" class="manual-section">
        <h2>Biblioteca</h2>
        
        <div class="feature-block">
          <h3>Navegação na Biblioteca</h3>
          <ul>
            <li><strong>Ordenação:</strong> Ordene por A-Z, número de capítulos, progresso de leitura ou favoritos</li>
            <li><strong>Tamanho dos Cards:</strong> Escolha entre pequeno, médio ou grande</li>
            <li><strong>Atualizar:</strong> Use a o botão atualizar para recarregar a informações da pasta onde está os mangás</li>
            <li><strong>Paginação:</strong> Configure quantos itens exibir por página</li>
          </ul>
        </div>

        <div class="feature-block">
          <h3>Detalhes do Mangá</h3>
          <ul>
            <li>Informações detalhadas (capítulos, páginas e progresso )</li>
            <li>Lista completa de capítulos</li>
            <li>Ordenação</li>
            <li>Atualizar:Use a o botão atualizar para recarregar a informações da pasta onde está os capítulos</li>
            <li>Progresso: Registre seu progresso na leitura</li>
            <li>Opção "Continuar Lendo" para retomar de onde parou</li>
          </ul>
        </div>
      </section>

      <section id="reader" class="manual-section">
        <h2>Leitor</h2>
        
        <div class="feature-block">
          <h3>Modos de Leitura</h3>
          <div class="reading-modes">
            <div class="mode-card">
              <h4>Modo Página Única (horizontal)</h4>
              <p>Exibe uma página por vez, ideal para mangás tradicionais</p>
            </div>
            <div class="mode-card">
              <h4>Modo Vertical</h4>
              <p>Páginas em sequência vertical, perfeito para webtoons</p>
            </div>
          </div>
        </div>

        <div class="feature-block">
          <h3>Controles do Leitor</h3>
          <ul>
            <li><strong>Navegação:</strong> Clique nas setas ou use as teclas direcionais</li>
            <li><strong>Zoom:</strong> Use a roda do mouse ou botões para aproximar</li>
            <li><strong>Tela Cheia:</strong> Pressione F11 ou clique no ícone de tela cheia</li>
            <li><strong>Menu Rápido:</strong> Clique no centro da tela para acessar controles</li>
          </ul>
        </div>
      </section>

      <section id="settings" class="manual-section">
        <h2>Configurações</h2>
        
        <div class="settings-grid">
          <div class="setting-category">
            <h3>Interface</h3>
            <ul>
              <li>Tamanho dos cards da biblioteca</li>
              <li>Itens por página</li>
              <li>Tema e cores</li>
            </ul> 
          </div>
          
          <div class="setting-category">
            <h3>Leitura</h3>
            <ul>
              <li>Modo de leitura padrão</li>
              <li>Ajuste padrão leitura</li>
              <li>Qualidade das imagens</li>
            </ul>
          </div>
          
          <div class="setting-category">
            <h3>Performance</h3>
            <ul>
              <li>Cache de imagens</li>
              <li>Pré-carregamento de páginas</li>
              <li>Otimizações de memória</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="shortcuts" class="manual-section">
        <h2>Atalhos de Teclado</h2>
        
        <div class="shortcuts-grid">
          <div class="shortcut-category">
            <h3>Navegação Geral</h3>
            <div class="shortcut-list">
              <div class="shortcut-item">
              </div>
              <div class="shortcut-item">
                <kbd>Esc</kbd>
                <span>Fechar modais/menus</span>
              </div>
              <div class="shortcut-item">
                <kbd>Alt + ←</kbd>
                <span>Voltar</span>
              </div>
            </div>
          </div>

          <div class="shortcut-category">
            <h3>Leitor</h3>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>←/→</kbd>
                <span>Página Anterior/Próxima</span>
              </div>
              <div class="shortcut-item">
                <kbd>↑/↓</kbd>
                <span>Rolar Página (Modo Vertical)</span>
              </div>
              <div class="shortcut-item">
                <kbd>h</kbd>
                <span>Abrir Menu Reader</span>
              </div>
              <div class="shortcut-item">
                <kbd>f</kbd>
                <span>Tela Cheia</span>
              </div>
              <div class="shortcut-item">
                <kbd>s</kbd>
                <span>Abrir Sidebar Settings</span>
              </div>
              <div class="shortcut-item">
                <kbd>Space</kbd>
                <span>Próxima página</span>
              </div>
            </div>
          </div>

          <div class="shortcut-category">
            <h3>Biblioteca</h3>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>F5</kbd>
                <span>Atualizar biblioteca</span>
              </div>
              <div class="shortcut-item">
                <kbd>Ctrl + F</kbd>
                <span>Buscar mangá</span>
              </div>
              <div class="shortcut-item">
                <kbd>Enter</kbd>
                <span>Abrir mangá selecionado</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="tips" class="manual-section">
        <h2>Dicas e Truques</h2>
        
        <div class="tips-grid">
          <div class="tip-card">
            <h3>Performance</h3>
            <ul>
              <li>Ative o cache de imagens para carregamento mais rápido</li>
              <li>Use pré-carregamento em conexões rápidas</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>Leitura</h3>
            <ul>
              <li>Use o modo vertical para webtoons e manhwas</li>
              <li>Experimente diferentes níveis de zoom para conforto</li>
              <li>O sistema salva automaticamente seu progresso</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>Organização</h3>
            <ul>
              <li>Organize por progresso de leitura para continuar onde parou</li>
              <li>Deixe suas pastas no formato correto (Veja em Setup)</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>Solução de Problemas</h3>
            <ul>
              <li>Limpe o cache se imagens não carregarem</li>
              <li>Reescaneie a biblioteca após adicionar novos arquivos</li>
              <li>Verifique as permissões de pasta se ocorrerem erros</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ManualView',
  methods: {
    scrollTo(elementId) {
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  },
  mounted() {
    document.title = 'Manual de Uso - Ohara';
  }
}
</script>

<style scoped>
.manual-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  padding: 20px;
}

.manual-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
}

.manual-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.manual-header p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

.manual-content {
  max-width: 1200px;
  margin: 0 auto;
}

.section-nav {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-nav h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.section-nav ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.section-nav a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: block;
}

.section-nav a:hover {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
  transform: translateX(5px);
}

.manual-section {
  margin-bottom: 50px;
  scroll-margin-top: 20px;
}

.manual-section h2 {
  font-size: 2rem;
  margin-bottom: 25px;
  color: #4ecdc4;
  border-bottom: 2px solid rgba(78, 205, 196, 0.3);
  padding-bottom: 10px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
}

.info-card h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.feature-block {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-block h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.feature-block ul {
  line-height: 1.8;
}

.feature-block li {
  margin-bottom: 8px;
}

.reading-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.mode-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mode-card h4 {
  color: #4ecdc4;
  margin-bottom: 10px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.setting-category {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.setting-category h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.shortcut-category {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.shortcut-category h3 {
  color: #4ecdc4;
  margin-bottom: 20px;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.shortcut-item:last-child {
  border-bottom: none;
}

kbd {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
  padding: 4px 8px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.9rem;
  border: 1px solid rgba(78, 205, 196, 0.3);
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.tip-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
}

.tip-card:hover {
  transform: translateY(-3px);
}

.tip-card h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.tip-card ul {
  line-height: 1.7;
}

.tip-card li {
  margin-bottom: 8px;
}

.manual-footer {
  text-align: center;
  margin-top: 50px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.manual-footer p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

/* Responsividade */
@media (max-width: 768px) {
  .manual-container {
    padding: 15px;
  }
  
  .manual-header h1 {
    font-size: 2rem;
  }
  
  .manual-section h2 {
    font-size: 1.5rem;
  }
  
  .content-grid,
  .settings-grid,
  .shortcuts-grid,
  .tips-grid {
    grid-template-columns: 1fr;
  }
  
  .section-nav ul {
    grid-template-columns: 1fr;
  }
  
  .reading-modes {
    grid-template-columns: 1fr;
  }
}

/* Animações suaves */
* {
  transition: all 0.3s ease;
}

/* Scrollbar personalizada */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(78, 205, 196, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(78, 205, 196, 0.7);
}
</style>