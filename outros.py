#Wifi:
import network
import socket
from time import sleep

def mudar(b:int, a:int,  n = 1):
    if a > b:
        return b + n
    if a < b:
        return b - n
    return b

def tempo_h_m_s(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos = segundos % 60
    return f"{horas} hora(s), {minutos} minuto(s) e {segundos} segundo(s)"

def criar_html(modo_global, freq_global, temperatura_global_1, temperatura_global_2, temperatura_placa, gc, memorias, memoria_uso, acoes):
    html = """
    <html>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>
        
        <head>   
            <meta content="width=device-width, initial-scale=1" name="viewport"></meta>   
        </head>

        <style>
        table, th, td {
          border: 1px solid black;
        }

        .grafico-par {
            display: flex;
            flex-wrap: wrap;
        }

        .grafico-container {
            flex-basis: calc(50% - 20px); /* Divide em duas colunas com espaço entre elas */
            padding: 10px;
            box-sizing: border-box;
        }

        .grafico {
            width: 100%;
            max-width: 100%;
        }

        @media screen and (max-width: 900px) {
            .grafico-container {
                flex-basis: 100%; /* Uma coluna em telas menores */
            }
        }
        </style>

        <body>
            <center><p>Ligado a <strong>""" + tempo_h_m_s(sum(memoria_uso.values()) * 10) + """</strong>.</p></center>
            <center><h2>Cafarnaum</h2></center>   
                <center>   
                 <form>   
                  <button name="MODO" type="submit" value="0"> OFF </button>   
                  <button name="MODO" type="submit" value="1"> ECO </button>
                  <button name="MODO" type="submit" value="2"> TURBO </button>
                  <button name="MODO" type="submit" value="3"> FULL </button>  
                 </form>   
                </center>   
            <center><p>Modo atual: <strong>""" + str(modo_global) + """</strong>.</p></center>
            <center><p>Frequência: <strong>""" + str(freq_global) + """</strong>.</p></center>
            <center><p>Potência: <strong>""" + str(int(pot_global/1024*100 + 0.5)) + """</strong>.</p></center>
            <center><p>Temperatura saída: <strong>""" + str(temperatura_global_1) + """</strong>.</p></center>
            <center><p>Temperatura da Placa: <strong>""" + str(temperatura_global_2) + """</strong>.</p></center>
            <center><p>Temperatura do Processador: <strong>""" + str(temperatura_placa) + """</strong>.</p></center>
            <center><p>Memória usada (kb): <strong>""" + str((512*1024 - gc.mem_alloc)/1024)[:6] + """/"""+ str(512) + """</strong>.</p></center>

            <br>

            <form>
                <input type="checkbox" id="automatizar" name="automatizar" value="1">
                <label for="vehicle1">Rodar automatização definida abaixo</label><br>
                  
                <label for="modo1">Ação 1 MODO e TEMPO (em minutos):</label>
                <select id="modo1" name="modo1">
                <option value="nada1" selected>NADA</option>
                    <option value="off1">OFF</option>
                    <option value="eco1">ECO</option>
                    <option value="turbo1">TURBO</option>
                    <option value="full1">FULL</option>
                  </select>
                  <input type="number" id="tempo1" name="tempo1" min="1" max="4320" value="1"> <p>

                <label for="modo2">Ação 2 MODO e TEMPO (em minutos):</label>
                <select id="modo2" name="modo1">
                <option value="nada2" selected>NADA</option>
                    <option value="off2">OFF</option>
                    <option value="eco2">ECO</option>
                    <option value="turbo2">TURBO</option>
                    <option value="full2">FULL</option>
                  </select>
                  <input type="number" id="tempo2" name="tempo2" min="1" max="4320" value="1"> <p>

                <label for="modo3">Ação 3 MODO e TEMPO (em minutos):</label>
                <select id="modo3" name="modo1">
                <option value="nada3" selected>NADA</option>
                    <option value="off3">OFF</option>
                    <option value="eco3">ECO</option>
                    <option value="turbo3">TURBO</option>
                    <option value="full3">FULL</option>
                  </select>
                  <input type="number" id="tempo3" name="tempo3" min="1" max="4320" value="1"> <p>

                <label for="modo4">Ação 4 MODO e TEMPO (em minutos):</label>
                <select id="modo4" name="modo1">
                <option value="nada4" selected>NADA</option>
                    <option value="off4">OFF</option>
                    <option value="eco4">ECO</option>
                    <option value="turbo4">TURBO</option>
                    <option value="full4">FULL</option>
                  </select>
                  <input type="number" id="tempo4" name="tempo4" min="1" max="4320" value="1"> <p>

                <label for="modo5">Ação 5 MODO e TEMPO (em minutos):</label>
                <select id="modo5" name="modo1">
                <option value="nada5" selected>NADA</option>
                    <option value="off5">OFF</option>
                    <option value="eco5">ECO</option>
                    <option value="turbo5">TURBO</option>
                    <option value="full5">FULL</option>
                  </select>
                  <input type="number" id="tempo5" name="tempo5" min="1" max="4320" value="1"> <p>

            <button type="submit">Salvar</button>
            <\form>

            <br>
            
            <h2>Automazização Atual:</h2>
            <table style="width:100%">
              <tr>
                <th>Ação</th> 
                <th>Modo</th> 
                <th>Tempo Dessa Ação (Minutos)</th>
                <th>Ativa no Momento</th>
              </tr>""" + acoes + """
            </table>


            <div class="grafico-par">
                <div class="grafico-container">
                    <canvas id="graficotemperatura" class="grafico"></canvas>
                </div>
                <div class="grafico-container">
                    <canvas id="graficopotencia" class="grafico"></canvas>
                </div>
            </div>

            <div class="grafico-par">
                <div class="grafico-container">
                    <canvas id="graficofrequencia" class="grafico"></canvas>
                </div>
                <div class="grafico-container">
                    <canvas id="myChart" class="grafico"></canvas>
                </div>
            </div>

            <script>
            const xValues = """ + str([i * -10 for i in range(len(memorias["temperatura_1"]))]) + """;

            new Chart("graficotemperatura", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{ 
                  data: """ + str(memorias["temperatura_1"]) + """,
                  borderColor: "blue",
                  fill: false,
                  label: "Saída" // Adicione o nome da série A aqui
                }, { 
                  data: """ + str(memorias["temperatura_2"]) + """,
                  borderColor: "green",
                  fill: false,
                  label: "Hardware" // Adicione o nome da série B aqui
                }, { 
                  data: """ + str(memorias["temperatura_3"]) + """,
                  borderColor: "red",
                  fill: false,
                  label: "Controlador"
                }]
              },
              options: {
                title: { 
                  display: true,
                  text: 'Temperaturas'
                },
                legend: {
                  display: true,
                  position: 'top',
                }
              }
            });


            new Chart("graficopotencia", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{ 
                  data: """ + str(memorias["potencia"]) + """,
                  borderColor: "red",
                  fill: false,
                  label: "Potência"
                }]
              },
              options: {
                title: { 
                  display: true,
                  text: 'Potência'
                },
                legend: {
                  display: false,
                  position: 'top',
                }
              }
            });


            new Chart("graficofrequencia", {
              type: "line",
              data: {
                labels: xValues,
                datasets: [{ 
                  data: """ + str(memorias["frequencia"]) + """,
                  borderColor: "red",
                  fill: false,
                  label: "Frequência"
                }]
              },
              options: {
                title: { 
                  display: true,
                  text: 'Frequência'
                },
                legend: {
                  display: false,
                  position: 'top',
                }
              }
            });


            const xValues2 = ["OFF", "ECO", "TURBO", "FULL", "PROGRAMADO", "RESFRIAR"];
            const yValues = """ + str(memoria_uso.values()) + """;
            const barColors = [
              "#808080",
              "#8ae580",
              "#e95151",
              "#feec35",
              "#16aeae"
            ];

            new Chart("myChart", {
              type: "pie",
              data: {
                labels: xValues2,
                datasets: [{
                  backgroundColor: barColors,
                  data: yValues
                }]
              },
              options: {
                title: {
                  display: true,
                  text: "Frequência de uso dos Modos (nos últimos """ + str(sum(memoria_uso.values()) * 10) + """ segundos)"
                }
              }
            });

            </script>
    
        </body>   
        </html>"""
    return html
