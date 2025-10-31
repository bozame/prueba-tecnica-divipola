# prueba-tecnica-divipola

para correrlo:

cd desktop-app

npm run tauri dev


Parte de mi solución era la siguiente: La app de escritorio tiene su base de datos persistente, que tiene una columna que la base de datos de la nube no tiene, la columna "estado", los datos que hayan sido traidos de la nube tienen como estado natural 1, los que vayan a ser enviados por medio de un POST tienen como estado 3, los que hayan sido actualizados tienen como estado 2, y los que fueron eliminados estado 0.

Por medio de la API se hace envío de los datos con estado diferente de 1, una vez confirmada la sincronización con la nube, los datos pasan todos a estado natural 1, excepto los que fueron eliminados. Se alojan en la tbala con estado 0 para luego poder indicarle a la nube que esos son los que desaparecerán, una vez sincronizadas ambas bases de datos las filas desaparecen de ambas tablas.

La API tiene un pequeño método get que funciona como un ping para determinar si hay conexión o no con la DB, este se envía cada 20 segundos automáticamente, también está el botón manual en caso de ser necesario. Si mo tiene conexión muestra un mensaje de "Sin conexión", y cuando vuelve a contectarse a internet incia el proceso de sincronización el solo.

Para evitar la duplicidad al momento de sincronizar las tablas cuando se creó la db local en Tauri (\src-tauri\src\lib.rs) se agregó una restricción con UNIQUE.

Tampoco permite duplicidad al intentar insertar dos veces la misma combinación de departamento-municipio-corregimiento, o simplemente departamento-municipio.

La db se desplegó en Railway usando MySQL, y la API está en el mismo proyecto conectado al repositorio de github.