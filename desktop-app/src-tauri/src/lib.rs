use tauri_plugin_sql::{Migration, MigrationKind};  

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let migrations = vec![
        Migration {
            version: 1,
            description: "create_divipola_table",
            sql: "
                CREATE TABLE IF NOT EXISTS divipola (
                    cod_pais TEXT,
                    cod_departamento TEXT,
                    cod_municipio TEXT,
                    nom_departamento TEXT,
                    nom_municipio TEXT,
                    nom_corregimiento TEXT,
                    estado INTEGER DEFAULT 0,
                    UNIQUE (cod_departamento, cod_municipio, nom_municipio, nom_corregimiento)
                );
            ",
            kind: MigrationKind::Up,
        },
    ];

    tauri::Builder::default()
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations("sqlite:divipola_local.db", migrations)
                .build(),
        )
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
