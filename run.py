from app import create_app

# Cria a instância da nossa aplicação
app = create_app()

if __name__ == '__main__':
    # O modo debug reinicia o servidor automaticamente ao salvarmos um arquivo
    app.run(debug=True, host='0.0.0.0', port=5000)