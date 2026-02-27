from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Crear las tablas en la base de datos si no existen
        db.create_all()
        print("Tablas creadas en la base de datos")
    # Ejecutar la aplicación Flask en modo de desarrollo
    print("Iniciando la aplicación Flask...")
    app.run(debug=True)