<template>
  <div class="app-container">
    <div class="left-panel">
      <h2>Registrar nuevo lugar</h2>

      <div class="form-group">
        <label>Departamento</label>
        <select v-model="departamentoSeleccionado" class="input-select">
          <option value="">Seleccionar departamento</option>
          <option v-for="dep in departamentos" :key="dep.cod_departamento" :value="dep">
            {{ dep.nom_departamento }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>Municipio</label>
        <select v-model="municipioSeleccionado" class="input-select">
          <option disabled value="">Seleccionar municipio</option>
          <option
            v-for="mun in municipios"
            :key="mun.cod_municipio"
            :value="mun.nom_municipio"
          >
            {{ mun.nom_municipio }}
          </option>
          <option value="nuevo">OTRO</option>
        </select>

        <small>¿No está en la lista?</small>
        <input
          type="text"
          placeholder="Escribir nuevo municipio"
          v-model="nuevoMunicipio"
          :disabled="municipioSeleccionado !== 'nuevo'"
        />
      </div>

      <div class="form-group">
        <label>Corregimiento (opcional)</label>
        <input type="text" placeholder="Seleccionar corregimiento" v-model="corregimiento" />
      </div>

      <button class="save-btn" @click="guardarRegistro">Guardar</button>

      <div class="sync-status" :class="syncStatusClass">
        {{ syncStatusText }}
      </div>

    </div>


    <div class="right-panel">
      <div class="actions">
        <button class="sync-btn" @click="sincronizarDesdeNube">Sincronizar</button>
        <button class="update-btn" :disabled="!filaSeleccionada" @click="openEdit">
          Actualizar
        </button>
        <button class="delete-btn" :disabled="!filaSeleccionada" @click="deleteSelected">
          Eliminar
        </button>
      </div>

      <div class="tabs">
        <button
          class="tab-btn"
          :class="{ active: pestañaActiva === 'todos' }"
          @click="pestañaActiva = 'todos'"
        >
          Todos los registros
        </button>
        <button
          class="tab-btn"
          :class="{ active: pestañaActiva === 'recientes' }"
          @click="pestañaActiva = 'recientes'"
        >
          Recientes
        </button>
      </div>

      <div v-if="pestañaActiva === 'todos'" class="table-container">
        <table>
          <thead>
            <tr>
              <th>País</th>
              <th>Código departamento</th>
              <th>Código municipio</th>
              <th>Departamento</th>
              <th>Municipio</th>
              <th>Corregimiento</th>
              <th>¿Sincronizado?</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(registro, index) in registros"
              :key="'all-' + index"
              @click="selectRow(registro)"
              :class="{
                hovered: filaResaltada === registro,
                selected: filaSeleccionada === registro,
              }"
              @mouseenter="filaResaltada = registro"
              @mouseleave="filaResaltada = null"
            >
              <td>{{ registro.cod_pais }}</td>
              <td>{{ registro.cod_departamento }}</td>
              <td>{{ registro.cod_municipio }}</td>
              <td>{{ registro.departamento }}</td>
              <td>{{ registro.municipio }}</td>
              <td>{{ registro.corregimiento }}</td>
              <td>{{ registro.sincronizar === 1 ? '✅' : '❌' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="pestañaActiva === 'recientes'" class="table-container">
        <table>
          <thead>
            <tr>
              <th>País</th>
              <th>Código departamento</th>
              <th>Código municipio</th>
              <th>Departamento</th>
              <th>Municipio</th>
              <th>Corregimiento</th>
              <th>¿Sincronizado?</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(registro, index) in recientes"
              :key="'rec-' + index"
              @click="selectRow(registro)"
              :class="{
                hovered: filaResaltada === registro,
                selected: filaSeleccionada === registro,
              }"
              @mouseenter="filaResaltada = registro"
              @mouseleave="filaResaltada = null"
            >
              <td>{{ registro.cod_pais }}</td>
              <td>{{ registro.cod_departamento }}</td>
              <td>{{ registro.cod_municipio }}</td>
              <td>{{ registro.departamento }}</td>
              <td>{{ registro.municipio }}</td>
              <td>{{ registro.corregimiento }}</td>
              <td>{{ registro.sincronizar === 1 ? '✅' : '❌' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="mostrarEditar" class="Edit-overlay">
      <div class="Edit">
        <h3>Editar registro</h3>

        <div class="form-group" v-for="(value, key) in editable" :key="key">
          <label :for="String(key)">{{ key }}</label>
          <input
            type="text"
            :id="String(key)"
            v-model="editable[key]"
            :readonly="key.startsWith('cod_')"
            :class="{ readonly: key.startsWith('cod_') }"
          />
        </div>

        <div class="Edit-actions">
          <button class="save-btn" @click="saveChanges">Guardar</button>
          <button class="delete-btn" @click="closeEdit">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, computed, watch } from "vue";
  import Database from "@tauri-apps/plugin-sql";

  interface Registro {
    cod_pais: string;
    cod_departamento: string;
    cod_municipio: string;
    departamento: string;
    municipio: string;
    corregimiento: string;
    sincronizar: number; // estado de sincronización
  }

  const registros = ref<Registro[]>([]);
  const recientes = ref<Registro[]>([]);
  const pestañaActiva = ref<"todos" | "recientes">("todos");
  const filaResaltada = ref<Registro | null>(null);
  const filaSeleccionada = ref<Registro | null>(null);
  const mostrarEditar = ref(false);
  const editable = reactive<any>({});
  const error = ref("");
  const departamentos = ref<Array<{ cod_departamento: string; nom_departamento: string; cod_pais?: string }>>([]);
  const departamentoSeleccionado = ref<{ cod_departamento: string; nom_departamento: string; cod_pais?: string } | null>(null);
  const municipios = ref<Array<{ cod_municipio: string; nom_municipio: string }>>([]);
  const municipioSeleccionado = ref<string>("");
  const nuevoMunicipio = ref("");
  const corregimiento = ref("");
  const sincronizando = ref(false);
  const syncStatusText = ref("Sincronización pendiente");
  const syncStatusClass = ref("");

  watch(departamentoSeleccionado, () => {
    cargarMunicipiosPorDepartamento()
    municipioSeleccionado.value = ''
    nuevoMunicipio.value = ''
  })

  watch(municipioSeleccionado, (nuevoNombre) => {
    if (nuevoNombre !== 'nuevo') nuevoMunicipio.value = ''
  })

  async function getDB() {
    return await Database.load("sqlite:divipola_local.db");
  }

  ////////////////////////// SINCRONIZAR CON LA NUBE
  async function sincronizarDesdeNube() {
    const db = await getDB();

    const pendientes = await db.select(`
      SELECT 
        cod_pais, cod_departamento, cod_municipio, 
        nom_departamento AS departamento, 
        nom_municipio AS municipio, 
        nom_corregimiento AS corregimiento,
        estado AS sincronizar
      FROM divipola
      WHERE estado != 1
    `);

    for (const reg of pendientes) {
      try {
        if (reg.sincronizar === 3) { //////////// POST
          const res = await fetch("https://prueba-tecnica-divipola-production.up.railway.app/divipola", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              cod_pais: reg.cod_pais,
              cod_departamento: reg.cod_departamento,
              cod_municipio: reg.cod_municipio,
              nom_departamento: reg.departamento,
              nom_municipio: reg.municipio,
              nom_corregimiento: reg.corregimiento || "",
            }),
          });

          const serverResp = await res.json().catch(() => ({}));
          console.log("Respuesta POST:", serverResp);

          if (res.ok) {
            await db.execute(`UPDATE divipola SET estado = 1 WHERE cod_departamento = ? AND cod_municipio = ?`, [reg.cod_departamento, reg.cod_municipio]);
            console.log(`Enviado a la nube: ${reg.municipio}`);
          }
        } else if (reg.sincronizar === 2) { /////////// PUT
          const res = await fetch(`https://prueba-tecnica-divipola-production.up.railway.app/divipola/${reg.cod_departamento}/${reg.cod_municipio}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              nom_departamento: reg.departamento,
              nom_municipio: reg.municipio,
              nom_corregimiento: reg.corregimiento || "",
            }),
          });

          const serverResp = await res.json().catch(() => ({}));
          console.log("Respuesta PUT: ", serverResp);

          if (res.ok) {
            await db.execute(`UPDATE divipola SET estado = 1 WHERE cod_departamento = ? AND cod_municipio = ?`, [reg.cod_departamento, reg.cod_municipio]);
          }
        } else if (reg.sincronizar === 0) {///////////////// DELETE
          const res = await fetch(`https://prueba-tecnica-divipola-production.up.railway.app/divipola/${reg.cod_departamento}/${reg.cod_municipio}`, { method: "DELETE" });
          if (res.ok) {
            await db.execute(`DELETE FROM divipola WHERE cod_departamento = ? AND cod_municipio = ?`, [reg.cod_departamento, reg.cod_municipio]);
          }
        }
      } catch (err) {
        console.error("Error sincronizando registro: ", reg, err);
      }
    }

    try {
      const res = await fetch("https://prueba-tecnica-divipola-production.up.railway.app/divipola");
      const data = await res.json();
      for (const lugar of data) {
        await db.execute(`INSERT OR IGNORE INTO divipola (cod_pais, cod_departamento, cod_municipio, nom_departamento, nom_municipio, nom_corregimiento, estado) VALUES (?, ?, ?, ?, ?, ?, 1)`, [
          lugar.cod_pais,
          lugar.cod_departamento,
          lugar.cod_municipio,
          lugar.nom_departamento,
          lugar.nom_municipio,
          lugar.nom_corregimiento,
        ]);
      }
      await cargarRegistros();
      console.log("Sincronización completada");
    } catch (err) {
      console.error("Error al traer datos de la nube:", err);
    }
  }

  ///////////////////// CARGAN LOS DATOS
  async function cargarRegistros() {
    try {
      const db = await getDB();
      const result = await db.select<Registro[]>(
        `SELECT 
          cod_pais, 
          cod_departamento, 
          cod_municipio, 
          nom_departamento AS departamento, 
          nom_municipio AS municipio, 
          nom_corregimiento AS corregimiento, 
          estado AS sincronizar 
        FROM divipola
        WHERE estado IN (1, 2, 3)`
      );

      registros.value = result;

      // pestaña de recientes
      recientes.value = result.filter((r) => r.sincronizar === 2 || r.sincronizar === 3);
    } catch (err) {
      console.error(err);
      error.value = "Error al cargar registros desde la db local";
    }
  }

  ///////////////// LISTADO DEPARTAMENTOS
  async function cargarDepartamentos() {
    try {
      const db = await getDB();
      const filas = await db.select<{ cod_departamento: string; nom_departamento: string; cod_pais: string }[]>(
        `SELECT DISTINCT cod_departamento, nom_departamento, cod_pais
        FROM divipola
        ORDER BY nom_departamento`
      );
      departamentos.value = filas || [];
    } catch (err) {
      console.error("Error al cargar departamentos: ", err);
    }
  }

  ///////////////////LISTADO MUNICIPIOS
  async function cargarMunicipiosPorDepartamento() {
    if (!departamentoSeleccionado.value) {
      municipios.value = [];
      return;
    }
    try {
      const db = await getDB();
      const filas = await db.select<{ cod_municipio: string; nom_municipio: string }[]>(
        `SELECT DISTINCT cod_municipio, nom_municipio
        FROM divipola
        WHERE cod_departamento = ?
        ORDER BY nom_municipio`,
        [departamentoSeleccionado.value.cod_departamento]
      );
      municipios.value = filas || [];
    } catch (err) {
      console.error("Error al cargar municipios:", err);
    }
  }

  /////////////////// GENERACION DE CÓDIGOS PARA MUNICIPIOS
  async function generarCodigoMunicipio(codDepartamento: string, nomMunicipio: string): Promise<string> {
      const db = await getDB();
      const res = await db.select<{ cod_municipio: string }[]>(
          `SELECT cod_municipio FROM divipola
          WHERE cod_departamento = ? AND nom_municipio = ?
          ORDER BY cod_municipio DESC LIMIT 1`,
          [codDepartamento, nomMunicipio]
      );

      const codDpto = codDepartamento.substring(0, 2); // dos primeros digitos siempre (en caso de que tenga mas de 2)

      if (res.length > 0) {
          const ultimoCodCompleto = res[0].cod_municipio.trim();
          const incrementarStr = ultimoCodCompleto.slice(-3);
          const incrementarInt = parseInt(incrementarStr, 10) || 0;
          const nuevoIncremental = (incrementarInt + 1).toString().padStart(3, '0'); 
          return codDpto + nuevoIncremental; 
      } else {
          const baseQuery = await db.select<{ cod_municipio: string }[]>(
              `SELECT cod_municipio FROM divipola 
              WHERE cod_departamento = ? AND nom_municipio = ? AND nom_corregimiento = '' 
              LIMIT 1`,
              [codDepartamento, nomMunicipio]
          );
          if (baseQuery.length > 0) {
              const maxCod = await db.select<{ max_cod: string }[]>(
                  `SELECT MAX(cod_municipio) AS max_cod FROM divipola 
                  WHERE cod_municipio LIKE ?`,
                  [codDpto + '%'] // Buscar el código más alto que empiece con el código del dpto (ej. 44%)
              );
              let incrementalInicial = 1;
              if (maxCod.length > 0 && maxCod[0].max_cod) {
                  const maxCod = maxCod[0].max_cod.trim();
                  const incrementarInt = parseInt(maxCod.slice(-3), 10) || 0;
                  incrementalInicial = incrementarInt + 1;
              }
              const nuevoincrementarStr = incrementalInicial.toString().padStart(3, '0'); 
              return codDpto + nuevoincrementarStr;
          } else {
              return codDpto + '001';
          }
      }
  }

  /////////////////////////// GUARDAR NUEVO REGISTRO
  async function guardarRegistro() {
    try {
      if (!departamentoSeleccionado.value) {
        alert("Debes seleccionar un departamento");
        return;
      }

      let municipioFinal = "";
      if (!municipioSeleccionado.value) {
        alert("Debes seleccionar o escribir un municipio");
        return;
      } else if (municipioSeleccionado.value === "nuevo") {
        municipioFinal = nuevoMunicipio.value.trim();
        if (!municipioFinal) {
          alert("Debes escribir el nombre del nuevo municipio");
          return;
        }
      } else {
        municipioFinal = municipioSeleccionado.value;
      }

      const corregimientoFinal = corregimiento.value.trim() || "";

      const codDepartamento = departamentoSeleccionado.value.cod_departamento;
      const nomDepartamento = departamentoSeleccionado.value.nom_departamento;
      const codPais = departamentoSeleccionado.value.cod_pais || "CO";

      const codMunicipio = await generarCodigoMunicipio(codDepartamento, municipioFinal);

      const nuevoCodigo = await generarCodigoMunicipio(codDepartamento, municipioFinal);
      const db = await getDB();
      await db.execute(
        `INSERT INTO divipola 
          (cod_pais, cod_departamento, cod_municipio, nom_departamento, nom_municipio, nom_corregimiento, estado) 
          VALUES (?, ?, ?, ?, ?, ?, 3)`,
        [
          departamentoSeleccionado.value.cod_pais,
          codDepartamento,
          nuevoCodigo,
          nomDepartamento,
          municipioFinal,
          corregimientoFinal,
        ]
      );

      alert(`Registro creado (pendiente de sincronizar)\nCódigo: ${codMunicipio}`);

      municipioSeleccionado.value = "";
      nuevoMunicipio.value = "";
      corregimiento.value = "";

      await cargarRegistros();
    } catch (err) {
      console.error("Error al guardar registro:", err);
      alert("Error al guardar registro. ver consola");
    }
  }



   ///////////////////////// EDITAR REGISTRO
  async function saveChanges() {
    if (!filaSeleccionada.value) return;
    const db = await getDB();
    if (!editable.corregimiento?.trim()) {
      const duplicado = await db.select(
        `SELECT 1 FROM divipola
        WHERE cod_departamento = ?
          AND UPPER(TRIM(nom_municipio)) = UPPER(?)
          AND (nom_corregimiento IS NULL OR TRIM(nom_corregimiento) = '')
          AND NOT (cod_departamento = ? AND cod_municipio = ?)
        LIMIT 1`,
        [
          editable.cod_departamento,
          editable.municipio,
          filaSeleccionada.value.cod_departamento,
          filaSeleccionada.value.cod_municipio,
        ]
      );

      if (duplicado.length > 0) {
        alert("Este municipio ya existe sin corregimiento, así que el corregimiento no se puede borrar");
        return;
      }
    }

    await db.execute(
      `UPDATE divipola 
      SET cod_pais = ?, cod_departamento = ?, cod_municipio = ?, 
          nom_departamento = ?, nom_municipio = ?, nom_corregimiento = ?, 
          estado = CASE WHEN estado = 1 THEN 2 ELSE estado END
      WHERE cod_departamento = ? AND cod_municipio = ?`,
      [
        editable.cod_pais,
        editable.cod_departamento,
        editable.cod_municipio,
        editable.departamento,
        editable.municipio,
        editable.corregimiento,
        filaSeleccionada.value.cod_departamento,
        filaSeleccionada.value.cod_municipio,
      ]
    );

    mostrarEditar.value = false;
    alert("Cambios guardados (pendiente de sincronizar)");
    await cargarRegistros();
  }

  ////////////////////// ELIMINAR
  async function deleteSelected() {
    if (!filaSeleccionada.value) return;
    const db = await getDB();

    await db.execute(
      `UPDATE divipola SET estado = 0 
      WHERE cod_departamento = ? AND cod_municipio = ?`,
      [filaSeleccionada.value.cod_departamento, filaSeleccionada.value.cod_municipio]
    );

    alert("Registro eliminado (pendiente de sincronizar)");
    await cargarRegistros();
    filaSeleccionada.value = null;
  }

  /////// pestañita de edición
  function openEdit() {
    if (filaSeleccionada.value) {
      Object.assign(editable, { ...filaSeleccionada.value });
      delete editable.sincronizar;
      mostrarEditar.value = true;
    }
  }

  function closeEdit() {
    mostrarEditar.value = false;
  }

  function selectRow(row: Registro) {
    filaSeleccionada.value = row;
  }
  async function verificarConexionYSincronizar() {
    if (sincronizando.value) return;
    sincronizando.value = true;
    try {
      const res = await fetch("https://prueba-tecnica-divipola-production.up.railway.app/ping");
      if (!res.ok) throw new Error("Servidor no disponible");

      
      console.log("Conexión activa, empezando sincronización");
      await sincronizarDesdeNube();
      console.log("Sincronización completada");
    } catch (err) {
      console.warn("No se pudo sincronizar:", err);
      syncStatusText.value = "No hay conexión a internet, no se pudo sincronizar";
      syncStatusClass.value = "error";
    } finally {
      sincronizando.value = false;
    }
  }

  onMounted(() => {
    cargarDepartamentos();
    cargarRegistros();
    setInterval(verificarConexionYSincronizar, 40000); // 60 segundos
  });
</script>


<style scoped>
  /*general*/
  .app-container {
    display: flex;
    height: 100vh;
    padding: 2rem;
    box-sizing: border-box;
    background-color: #f8f7fb;
    gap: 2rem;
    font-family: "Segoe UI", sans-serif;
  }

  /*panel izquierdo*/
  .left-panel {
    flex: 0.23;
    background-color: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 4px 10px rgba(96, 72, 144, 0.15);
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }

  .left-panel h2 {
    color: #5b3e96;
    margin-bottom: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 1rem;
  }

  label {
    font-weight: 600;
    color: #4a3b6e;
    margin-bottom: 0.3rem;
  }

  input {
    padding: 0.6rem 0.8rem;
    border: 1px solid #d0c7e3;
    border-radius: 0.5rem;
    outline: none;
    transition: 0.2s;
  }

  input:focus {
    border-color: #7b5cc5;
    box-shadow: 0 0 4px rgba(123, 92, 197, 0.3);
  }

  /*botones*/
  .save-btn {
    margin-top: 1rem;
    padding: 0.8rem;
    border: none;
    border-radius: 0.5rem;
    background-color: #7b5cc5;
    color: white;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    transition: background 0.2s;
  }

  .save-btn:hover {
    background-color: #6c4bb5;
  }

  .sync-btn {
    background-color: #61b968ff;
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.6rem 1.2rem;
    cursor: pointer;
    font-weight: 600;
  }

  .sync-btn:hover {
    background-color: #63a568ff;
  }

  .delete-btn {
    background-color: #e07b7b;
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.6rem 1.2rem;
    cursor: pointer;
    font-weight: 600;
  }

  .delete-btn:hover {
    background-color: #d46363;
  }

  .update-btn {
    background-color: #929292ff;
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.6rem 1.2rem;
    cursor: pointer;
    font-weight: 600;
  }

  .update-btn:hover {
    background-color: #636363ff;
  }

  /*panel derecho*/
  .right-panel {
    flex: 0.65;
    background-color: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 4px 10px rgba(96, 72, 144, 0.15);
    display: flex;
    flex-direction: column;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  /*tabs*/
  .tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .tab-btn {
    flex: 1;
    padding: 0.7rem;
    border: none;
    border-radius: 0.5rem;
    background-color: #ede9f7;
    color: #5b3e96;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .tab-btn.active {
    background-color: #7b5cc5;
    color: white;
  }

  /*tabla*/
  .table-container {
    flex: 1;
    overflow: auto;
    border: 1px solid #e0d8f2;
    border-radius: 0.5rem;
  }

  table {
    width: 100%;
    table-layout: auto;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.95rem;
  }


  thead {
    background-color: #f1ecfa;
  }

  th,
  td {
    padding: 0.8rem;
    border-bottom: 1px solid #e9e3f6;
  }

  tr.hovered {
    background-color: #f6f2ff;
  }

  tr.selected {
    background-color: #e7d9ff !important;
  }

  /*Edit*/
  .Edit-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(50, 40, 70, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(2px);
  }

  .Edit {
    background-color: white;
    padding: 2rem;
    border-radius: 1rem;
    width: 400px;
    box-shadow: 0 4px 10px rgba(96, 72, 144, 0.3);
    animation: fadeIn 0.3s ease;
  }

  .Edit h3 {
    margin-bottom: 1rem;
    color: #5b3e96;
    text-align: center;
  }

  .Edit-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 1.5rem;
  }

  /* Animación */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .left-panel select.input-select {
    width: 100%;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    border: 1px solid #ccc;
    background-color: #fff;
    font-size: 0.95rem;
    appearance: none; /* Quitar estilo por defecto */
    -webkit-appearance: none;
    -moz-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg fill='gray' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.8rem center;
    background-size: 1rem;
    cursor: pointer;
    transition: border 0.2s, box-shadow 0.2s;
  }

  .left-panel select.input-select:focus {
    border-color: #805ad5; /* violeta suave */
    box-shadow: 0 0 0 2px rgba(128, 90, 213, 0.2);
    outline: none;
  }

  .left-panel option {
    padding: 0.5rem;
  }

  input.readonly {
    background-color: #f0f0f0;
    opacity: 0.6;
    cursor: not-allowed;
  }


  .sync-status {
    margin-top: 1rem;
    font-weight: bold;
  }

  .sync-status.success {
    color: #2ecc71;
  }

  .sync-status.error {
    color: #e74c3c;
  }
</style>