const btn = document.querySelector("#pywebview_btn");
const post_btn = document.querySelector('#pywebview_postBtn');
const canvas =document.querySelector('#js_canvas');
const ctx = canvas.getContext('2d');
const match_selector = document.querySelector("#match_selector");
const logger = document.querySelector("#log_parent");
const debugger_div = document.querySelector("#debugger_area");
const response_viewer = document.querySelector('#response_viewer');
const action_type = ['待機', '移動', '建築', '破壊'];
const action_dir = ['無向','左上', '上', '右上', '右', '右下', '下', '左下', '左'];

let connectId = 10;
let token = 'token1';
let interval_id = -1;
let match_list = [];
let shown_log_id = [];

// 画像読み込み
const sprite = {
    craftsman: new Image(),
    castle: new Image(),
    wall: new Image(),
  };
  sprite.craftsman.src = "/static/img/craftsman.png";
  sprite.castle.src = "/static/img/castle.png";
  sprite.wall.src = "/static/img/wall.jpg";
  
  // 競技フィールドのクラス
  class Field {
    #canvas;
    #ctx;
    #cellSize;
    #board;
    #fstFlag;
    constructor() {
      this.#fstFlag = true;
    }
  
    init() {
      // キャンバス要素の初期設定
      this.#canvas = canvas;
      this.#canvas.width = 500;
      this.#canvas.height = 500;
      this.#ctx = ctx;
      this.#cellSize = this.#canvas.width / this.#board.width;
    }
  
    // 状態の取得と反映
    update(data) {
      if (this.#fstFlag) {
        this.#board = data.board;
  
        this.init();
        this.#fstFlag = false;
      }
      this.draw(this.process_field(this.#board));
    }
  
    process_field(board){
      let field = Array()
      for(let i = 0; i < board.height; i++){
        field.push(Array());
        for(let j = 0; j < board.width; j++){
          let structure = board.structures[i][j];
          let wall = board.walls[i][j];
          let territory = board.territories[i][j];
          let mason = board.masons[i][j];
          let region = {
            'structure': structure,
            'wall': wall,
            'territory': territory,
            'mason': mason
          };
          field[i].push(region);
        }
      }
      return field;
    }
  
    // フィールドの描画
    draw(field) {
      this.clear();
      this.#ctx.save();
      for(let y = 0; y < this.#board.height; y++){
        for(let x = 0; x < this.#board.width; x++){
          let r = field[y][x];
          // チーム属性
          if (r.territory != 0) {
            let colors = ["#ccc", "#fcc", "#cfc", "#ffc"];
            this.#ctx.save();
            this.#ctx.beginPath();
            this.#ctx.fillStyle = colors[r.territory];
            this.#ctx.rect(
              x * this.#cellSize + 1, y * this.#cellSize + 1,
              this.#cellSize - 2, this.#cellSize - 2
            );
            this.#ctx.fill();
            this.#ctx.restore();
          }
          // 属性 (中立、陣地、城壁)
          if (r.wall != 0) {
            this.#ctx.save();
            this.#ctx.drawImage(
              sprite.wall,
              x * this.#cellSize + 4, y * this.#cellSize + 4,
              this.#cellSize - 8, this.#cellSize - 8
            )
            this.#ctx.restore();
          }
          // 職人
          if (r.mason != 0) {
            this.#ctx.save();
            //this.#ctx.beginPath();
            this.#ctx.fillStyle = (r.mason > 0 ? "#a00" : "#0a0");
            this.#ctx.font = "bold 20pt sans-serif";
            this.#ctx.textAlign = "center";
            this.#ctx.textBaseline = "middle";
            this.#ctx.drawImage(
              sprite.craftsman,
              x * this.#cellSize + 1, y * this.#cellSize + 1,
              this.#cellSize - 2, this.#cellSize - 2
            )
            this.#ctx.fillText(
              r.mason,
              (x + 0.5) * this.#cellSize, (y + 0.5) * this.#cellSize
            );
            this.#ctx.restore();
          }
          // 池
          if (r.structure == 1) {
            this.#ctx.save();
            this.#ctx.beginPath();
            this.#ctx.fillStyle = "#aaf";
            this.#ctx.rect(
              x * this.#cellSize + 1, y * this.#cellSize + 1,
              this.#cellSize - 2, this.#cellSize - 2
            );
            this.#ctx.fill();
            this.#ctx.restore();
          }
          // 城
          if (r.structure == 2) {
            this.#ctx.save();
            this.#ctx.drawImage(
              sprite.castle,
              x * this.#cellSize + 1, y * this.#cellSize + 1,
              this.#cellSize - 2, this.#cellSize - 2
            )
            this.#ctx.restore();
          }
        }
      }
      this.#ctx.restore();
      this.drawBorders();
    }
  
    // フィールドの表示初期化
    clear() {
      this.#ctx.save();
      this.#ctx.fillStyle = "#fff";
      this.#ctx.rect(0, 0, this.#canvas.width, this.#canvas.height);
      this.#ctx.fill();
      this.#ctx.restore();
    }
  
    // フィールドの枠線の描画
    drawBorders() {
      this.#ctx.save();
      this.#ctx.strokeStyle = "#000";
      this.#ctx.lineWidth = 1;
      for (let i = 0; i <= this.#board.width; i++) {
        this.#ctx.beginPath();
        this.#ctx.moveTo(0, this.#cellSize * i);
        this.#ctx.lineTo(this.#canvas.width, this.#cellSize * i);
        this.#ctx.stroke();
        this.#ctx.beginPath();
        this.#ctx.moveTo(this.#cellSize * i, 0);
        this.#ctx.lineTo(this.#cellSize * i, this.#canvas.height);
        this.#ctx.stroke();
      }
      this.#ctx.restore();
    }
  }
  

function drawGrid(rows, cols) {
    for(let row = 0; row < rows; row++){
        for(let col = 0; col < cols; col++){
            const x = col * colSize;
            const y = row * rowSize;

            ctx.strokeRect(x, y, colSize, rowSize);
        }
    }
}

function update_map_data(response) {
    let field = new Field();
    field.update(response);
    let cols = response.board.height;
    let rows = response.board.width;
    rowSize = canvas.height/cols;
    colSize = canvas.width/rows;

}

function updateLog(log){
  for(let i = 0; i < log.length; i++){
    line = log[i];
    if (!shown_log_id.includes(line['turn'])){
      element = getLogElement(line);
      logger.prepend(element);
      shown_log_id.push(line['turn']);
    }
  }
}

function getLogElement(log_line){
  let actions = log_line['actions'];
  let actions_text = '';
  for(let i = 0; i < actions.length; i++){
    if (i != 0) actions_text += `<br>`;
    let a = actions[i];
    actions_text += `行動:${action_type[a['type']]}, 方向:${action_dir[a['dir']]}, 結果:${a['succeeded'] ? '成功': '失敗'}`;
  }
  let result = document.createElement('div');
  result.classList.add('accordion-item');
  result.innerHTML = `
    <h2 class="accordion-header">
        <button class="accordion-header accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#log_collapse_${log_line['turn']}" aria-expanded="false" aria-controls="log_collapse_${log_line['turn']}">
            Log#${log_line['turn']}
        </button>
    </h2>
    <div id="log_collapse_${log_line['turn']}" class="accordion-collapse collapse" data-bs-parent="#log_parent">
        <div class="accordion-body">
            ${actions_text}
        </div>
    </div>
  `;
  return result;
}

document.querySelector("#get_match_list_button").addEventListener("click", function(){
  token = document.querySelector("#token_input").value;
  if(interval_id != -1) clearInterval(interval_id);
  $.ajax({
    type: 'get',
    url: '/matches',
    data:{
      'procon-token': token
    }
  }).done((data, status, xhr) => {
    data = JSON.parse(data);
    console.log(JSON.stringify(data));
    let selectHTML = "";
    for(let i = 0; i < data.matches.length; i++){
      match_list.push({
          'id': data.matches[i].id,
          'turns': data.matches[i].turns,
          'turnSec': data.matches[i].turnSeconds,
          'mason': data.matches[i].board.mason,
          'opponent': data.matches[i].opponent
      });
      selectHTML += `<option value="${match_list[i].id}">id: ${match_list[i].id}, 相手チーム: ${match_list[i].opponent}</option>`;
      logger.innerHTML = '';
    }
    match_selector.innerHTML = selectHTML;
  }).fail((err) => {
    debugger_div.innerHTML = err.responseText;
    console.log(err.status_code);
  });
});

function update_board(){
  $.ajax({
    type: 'get',
    url: '/match',
    data: {
      'procon-token': token,
      'match_id': connectId
    }
  }).done((data, status, xhr) => {
    if(data == "Too early") return;
    let res_json = data;
    update_map_data(res_json);
    updateLog(res_json['logs']);
  }).fail((err) => {
    debugger_div.innerHTML = err.responseText;
    console.log(err.status_code);
    clearInterval(interval_id);
  });
  $.ajax({
    type: 'get',
    url: '/controller'
  }).done((data) => {
    console.log(data);
    response_viewer.innerHTML = `<pre>${JSON.stringify(data.mason_list, null, 2)}</pre>`;
  })
}

document.querySelector("#get_match_info_button").addEventListener("click", function(){
  connectId = +document.querySelector("#match_selector").value;
  update_board();
  interval_id = setInterval(update_board, 1000);
});

canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const clickedRow = Math.floor(mouseY / rowSize);
    const clickedCol = Math.floor(mouseX / colSize);

    console.log(`cliked:${clickedRow},${clickedCol}`);
})
