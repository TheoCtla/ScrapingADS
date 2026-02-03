

echo "🚀 Démarrage complet du projet ScrappingRapport..."
echo "=================================================="


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 


print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}


if [ ! -f ".env" ]; then
    print_error "Fichier .env manquant !"
    print_warning "Créez-le avec les variables d'environnement nécessaires, aidez vous de .env.exemple.txt"
    print_warning "Voir la documentation pour les variables requises"
    exit 1
fi


if [ ! -f "backend/config/credentials.json" ]; then
    print_error "Fichier credentials.json manquant !"
    print_warning "Suivez les instructions dans CREDENTIALS_INSTRUCTIONS.md"
    exit 1
fi

print_status "✅ Vérifications des fichiers de configuration terminées"


cleanup() {
    print_status "🧹 Nettoyage des processus existants..."
    
    
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "flask" 2>/dev/null || true
    
    
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm.*dev" 2>/dev/null || true
    
    sleep 2
}


start_backend() {
    print_status "🔥 Démarrage du backend Flask..."
    
    
    cd backend
    ./venv/bin/python3 main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo $BACKEND_PID > backend.pid
    
    print_success "Backend démarré (PID: $BACKEND_PID)"
}


start_frontend() {
    print_status "🎨 Démarrage du frontend React..."
    
    
    cd frontend
    
    
    npm run dev > ../frontend.log 2>&1 &
    
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    print_success "Frontend démarré (PID: $FRONTEND_PID)"
}


check_services() {
    print_status "🔍 Vérification des services..."
    
    
    sleep 5
    
    
    if lsof -i :5050 > /dev/null 2>&1; then
        print_success "✅ Backend Flask actif sur http://localhost:5050"
    else
        print_error "❌ Backend non démarré"
        return 1
    fi
    
    
    if lsof -i :3000 > /dev/null 2>&1; then
        print_success "✅ Frontend React actif sur http://localhost:3000"
    else
        print_error "❌ Frontend non démarré"
        return 1
    fi
    
    return 0
}


show_info() {
    echo ""
    echo "🎉 PROJET DÉMARRÉ AVEC SUCCÈS !"
    echo "================================"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:5050"
    echo ""
    echo "📋 Logs disponibles:"
    echo "   - Backend: tail -f backend.log"
    echo "   - Frontend: tail -f frontend.log"
    echo ""
    echo "🛑 Pour arrêter: ./stop_project.sh"
    echo ""
}


cleanup_on_exit() {
    print_status "Arrêt en cours..."
    
    
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
    fi
    
    print_success "Projet arrêté proprement"
    exit 0
}


trap cleanup_on_exit SIGINT SIGTERM


main() {
    cleanup
    start_backend
    start_frontend
    
    if check_services; then
        show_info
        
        
        print_status "Appuyez sur Ctrl+C pour arrêter le projet..."
        while true; do
            sleep 1
        done
    else
        print_error "Échec du démarrage des services"
        cleanup_on_exit
    fi
}


main 