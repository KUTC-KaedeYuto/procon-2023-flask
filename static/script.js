const btn = document.querySelector("#pywebview_btn");
const post_btn = document.querySelector('#pywebview_postBtn');
const canvas =document.querySelector('#js_canvas');
const ctx = canvas.getContext('2d');
const match_selector = document.querySelector("#match_selector");
const logger = document.querySelector("#log_parent");
const debugger_div = document.querySelector("#debugger_area");
const response_viewer = document.querySelector('#response_viewer');
const mason_selector = document.querySelector('#mason_selector');
const allocate_button = document.querySelector("#allocate_button");
const mason_action_selector = document.querySelector("#mason_action_selector");
const dist_x = document.querySelector("#dist_x");
const dist_y = document.querySelector("#dist_y");
const mason_action_list = document.querySelector("#mason_action_list");
const delete_collapse = document.querySelector("#delete_collapse");
const edit_collapse = document.querySelector("#edit_collapse");
const delete_action_button = document.querySelector("#delete_action_button");
const edit_action_button = document.querySelector("#edit_action_button");
const swap_up_action_button = document.querySelector("#swap_up_action_button");
const swap_down_action_button = document.querySelector("#swap_down_action_button");
const action_type = ['待機', '移動', '建築', '破壊'];
const action_dir = ['無向','左上', '上', '右上', '右', '右下', '下', '左下', '左'];

var point_f = 0
var point_e = 0
const point_disp_f = document.querySelector("#flendlyteam_point")
const point_disp_e = document.querySelector("#enemyteam_point")

let connectId = 10;
let token = 'token1';
let interval_id = -1;
let match_list = [];
let shown_log_id = [];
let controller;
let field;
let last_clicked_action_id = -1;

// 画像読み込み
const sprite = {
    craftsman: new Image(),
    castle: new Image(),
    wall: new Image(),
    wall_red: new Image(),
    wall_green: new Image(),
    cursor: new Image(),
    flag: new Image(),
    plus: new Image(),
    hammer: new Image()
  };
sprite.craftsman.src = "/static/img/craftsman.png";
sprite.castle.src = "/static/img/castle.png";
sprite.wall.src = "/static/img/wall.jpg";
sprite.wall_red.src = "/static/img/wall_red.png";
sprite.wall_green.src = "/static/img/wall_green.png";
sprite.cursor.src = "/static/img/selected.png";
sprite.flag.src = "/static/img/flag.png";
sprite.plus.src = "/static/img/plus.png";
sprite.hammer.src = "/static/img/hammer.png";

  
  // 競技フィールドのクラス
  class Field {
    #canvas;
    #ctx;
    #cellSize;
    #board;
    #fstFlag;
    #clicked;
    #shown_icons;

    constructor() {
      this.#fstFlag = true;
      this.#shown_icons = [];
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
      this.#board = data.board;
      if (this.#fstFlag) {
        this.init();
        this.#fstFlag = false;
      }
      this.draw(this.process_field(this.#board));
    }
  
    process_field(board){
      let field = Array()
      point_f = 0
      point_e = 0
      for(let i = 0; i < board.height; i++){
        field.push(Array());
        for(let j = 0; j < board.width; j++){
          let structure = board.structures[i][j];
          let wall = board.walls[i][j];
          let territory = board.territories[i][j];
          let mason = board.masons[i][j];
          
          if (structure == 2 && territory == 1) point_f += 100
          else if (territory == 1) point_f += 10
          if (structure == 2 && territory == 2) point_e += 100
          else if (territory == 2) point_e += 10
          if (wall == 1) point_f += 30
          if (wall == 2) point_e += 30

          let region = {
            'structure': structure,
            'wall': wall,
            'territory': territory,
            'mason': mason
          };
          field[i].push(region);
        }
      }
      
      point_disp_f.innerHTML = "味方チーム:" + point_f
      point_disp_e.innerHTML = "敵チーム:" + point_e

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
            let colors = ["#ccc", "#cfc", "#fcc", "#ffc"];
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
          // 池
          if (r.structure == 1) {
            this.#ctx.save();
            this.#ctx.beginPath();
            this.#ctx.fillStyle = "#aaf";
            this.#ctx.rect(
              x * this.#cellSize + 3, y * this.#cellSize + 3,
              this.#cellSize - 6, this.#cellSize - 6
            );
            this.#ctx.fill();
            this.#ctx.restore();
          }
          // 属性 (中立、陣地、城壁)
          if (r.wall != 0) {
            this.#ctx.save();
            if (r.wall == 2) {
              this.#ctx.drawImage(
                sprite.wall_red,
                x * this.#cellSize + 7, y * this.#cellSize + 7,
                this.#cellSize - 14, this.#cellSize - 14
              )
            }
            else {
              this.#ctx.drawImage(
                sprite.wall_green,
                x * this.#cellSize + 7, y * this.#cellSize + 7,
                this.#cellSize - 14, this.#cellSize - 14
              )
            }
            this.#ctx.restore();
          }
          // 城
          if (r.structure == 2) {
            this.#ctx.save();
            this.#ctx.drawImage(
              sprite.castle,
              x * this.#cellSize + 1, y * this.#cellSize + 1,
              this.#cellSize - 2, this.#cellSize - 2
            );
            this.#ctx.restore();
          }
          // 職人
          if (r.mason != 0) {
            this.#ctx.save();
            //this.#ctx.beginPath();
            this.#ctx.fillStyle = (r.mason > 0 ? "#0a0" : "#a00");
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
        }
      }          
      //アイコン
      this.#ctx.save();
      this.#ctx.globalAlpha = 0.8;
      
      for(let d of this.#shown_icons){
        this.#ctx.drawImage(
          d.sprite,
          d.x * this.#cellSize + 1, d.y * this.#cellSize + 1,
          this.#cellSize - 2, this.#cellSize - 2
        );
      }
      this.#ctx.restore();

      //カーソル
      if(this.#clicked != null){
        let x = this.#clicked.x, y =this.#clicked.y;
        this.#ctx.drawImage(
          sprite.cursor,
          x * this.#cellSize + 1, y * this.#cellSize + 1,
          this.#cellSize - 2, this.#cellSize - 2
        );
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

    onClick(x, y){
      this.#clicked = {
        'x': x,
        'y': y
      };
      this.draw(this.process_field(this.#board));
    }

    drawIcon(x, y, sprite){
      this.#shown_icons.push({
        'x': x,
        'y': y,
        'sprite': sprite
      });
      this.draw(this.process_field(this.#board));
    }

    clearIcon(){
      this.#shown_icons = [];
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
    if(field == null) {
      field = new Field();
      let cols = response.board.height;
      let rows = response.board.width;
      rowSize = canvas.height/cols;
      colSize = canvas.width/rows;
    }
    field.update(response);
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

function updateMasonSelector(){
  result = '';
  for(let i = 0; i < mason_list.length; i++){
    let mason = mason_list[i];
    result += `<option value="${mason.id}">id:${mason.id}, pos:(${mason.location.x}, ${mason.location.y})</option>`;
  }
  mason_selector.innerHTML = result;
}

function updateMasonList(){
  mason_list = controller.mason_list;
  let value = +mason_selector.value;
  if(value >= 1) showActions(controller.mason_list[value - 1]);
}


function showActions(mason){
  const action_map = {
    'WaitAction':{
      display: '待機',
    },
    'MoveAction': {
      display: '移動',
      sprite: sprite.flag
    },
    'BuildAction': {
      display: '建築',
      sprite: sprite.plus
    },
    'DestroyAction': {
      display: '破壊',
      sprite: sprite.hammer
    }
  };
  field.clearIcon();
  let result = '';
  for(let i = mason.action_index; i < mason.actions.length; i++){
    let action = mason.actions[i];
    let item =
`<li class="list-group-item${i == mason.action_index ? " active" : ""}${i == last_clicked_action_id ? " list-group-item-info" : ""}"  data-action_id=${i}>
    行動:${action_map[action.type].display}, 目的地:(${action.dist.x},${action.dist.y})
</li>`;
    result += item;
    if(i == mason.action_index && action.type != 'WaitAction'){
      field.drawIcon(action.dist.x, action.dist.y, action_map[action.type].sprite);
    }
  }
  mason_action_list.innerHTML = result;
  for(let child of mason_action_list.children) {
    child.addEventListener("click", function(){onClickAction(this);});
  }
}

function onClickAction(element){
  if(last_clicked_action_id != -1) {
    for(let child of mason_action_list.children){
      if(+child.dataset.action_id == last_clicked_action_id){
        child.classList.remove("list-group-item-info");
        break;
      }
    }
  }
  if(+element.dataset.action_id == last_clicked_action_id){
    edit_collapse.classList.add("d-none");
    delete_collapse.classList.add("d-none");
    last_clicked_action_id = -1;
  }else {
    delete_collapse.classList.remove("d-none");
    if(element === mason_action_list.children[0]){
      edit_collapse.classList.add("d-none");
    }else{
      element.classList.add("list-group-item-info");
      edit_collapse.classList.remove("d-none");
    }
    last_clicked_action_id = +element.dataset.action_id;
  }
  
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
    update_map_data(data);
    updateMasonList();
    updateLog(data['logs']);
  }).fail((err) => {
    debugger_div.innerHTML = err.responseText;
    console.log(err.status_code);
    clearInterval(interval_id);
  });
  $.ajax({
    type: 'get',
    url: '/controller'
  }).done((data) => {
    controller = data;
    response_viewer.innerHTML = `<pre>${JSON.stringify(data.mason_list, null, 2)}</pre>`;
  });
}

document.querySelector("#get_match_info_button").addEventListener("click", function(){
  connectId = +document.querySelector("#match_selector").value;
  if (interval_id != -1) clearInterval(interval_id);
  update_board();
  interval_id = setInterval(update_board, 1000);
});

document.querySelector("#update_mason_button").addEventListener("click", updateMasonSelector);
document.querySelector("#select_mason_button").addEventListener("click", function(){
  document.querySelector("#mason_controller").classList.remove("d-none");
  document.querySelector("#mason_action_editor").classList.remove("d-none");
  let value = +mason_selector.value;
  showActions(controller.mason_list[value - 1]);
});

allocate_button.addEventListener("click", function(){
  allocate_button.disabled = true;
  $.ajax({
    type: 'POST',
    url  : '/allocate',
    headers: {
      'Content-Type': 'application/json'
    },
    data: JSON.stringify({
      'mason_id': +mason_selector.value,
      'action_type': mason_action_selector.value,
      'action_data': {
          'x': +dist_x.value,
          'y': +dist_y.value
      }
    })
  }).done((data, status, xhr) => {
    allocate_button.disabled = false;
    updateMasonList();  
  }).fail((err) => {
    allocate_button.disabled = false;
  });
});

delete_action_button.addEventListener("click", function(){
  data = {
    mason_id: +mason_selector.value,
    method: 'delete',
    option: {
      index: last_clicked_action_id
    }
  };
  for(let child of mason_action_list.children){
    if(+child.dataset.action_id == last_clicked_action_id) {
      onClickAction(child);
      break;
    }
  }
  $.ajax({
    type: 'POST',
    url: '/change',
    headers: {
      'Content-Type': 'application/json'
    },
    data: JSON.stringify(data)
  }).done((data, status, xhr) => {
    updateMasonList();
    console.log(data);
  });
});

document.querySelector("#test_button")?.addEventListener("click", () => {
  fetch("/test");
});

canvas.addEventListener("click", (e) => {
    if(field == null) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const clickedRow = Math.floor(mouseY / rowSize);
    const clickedCol = Math.floor(mouseX / colSize);

    console.log(`cliked:${clickedRow},${clickedCol}`);
    field.onClick(clickedCol, clickedRow);
    dist_x.value = clickedCol;
    dist_y.value = clickedRow;
});
