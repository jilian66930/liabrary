let primaryMatrixCounter = 0; // 用于生成唯一的一级指标矩阵 ID
let secondaryMatrixCounter = 0; // 用于生成唯一的二级指标矩阵 ID
const primaryMatrices = []; // 存储所有一级指标矩阵的信息
const secondaryMatrices = []; // 存储所有二级指标矩阵的信息
const fuzzyevaluationMatrices = []; // 存储所有模糊评价矩阵信息
let Fuzzy_Evaluation_MatrixCounter = 0; // 用于生成唯一的模糊评价矩阵 ID

function addPrimaryMatrix() {
    console.log("addPrimaryMatrix called"); // 调试信息
    const rows = parseInt(prompt("请输入一级指标矩阵的行数:"));
    const cols = parseInt(prompt("请输入一级指标矩阵的列数:"));

    if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
        alert("输入无效！请输入正整数。");
        return;
    }

    // 生成唯一的一级指标矩阵 ID
    const matrixId = `primary-matrix-${primaryMatrixCounter++}`;

    // 创建矩阵的 HTML
    const matrixHTML = `
        <div class="matrix-container" id="${matrixId}">
            <div class="matrix-input">
                <label>一级指标矩阵 ${matrixId}:</label>
                <br> <!-- 添加换行 -->
                ${generateMatrixInput(rows, cols, matrixId)} <!-- 显示矩阵输入 -->
            </div>
            <button type="button" onclick="deleteMatrix('${matrixId}', primaryMatrices)">删除矩阵</button>
        </div>
    `;

    document.getElementById("primary-matrices-container").insertAdjacentHTML("beforeend", matrixHTML);

    // 存储矩阵信息
    primaryMatrices.push({ id: matrixId, rows, cols });
}

function addSecondaryMatrix() {
    const rows = parseInt(prompt("请输入二级指标矩阵的行数:"));
    const cols = parseInt(prompt("请输入二级指标矩阵的列数:"));

    if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
        alert("输入无效！请输入正整数。");
        return;
    }

    // 生成唯一的二级指标矩阵 ID
    const matrixId = `secondary-matrix-${secondaryMatrixCounter++}`;

    // 创建矩阵的 HTML
    const matrixHTML = `
        <div class="matrix-container" id="${matrixId}">
            <div class="matrix-input">
                <label>二级指标矩阵 ${matrixId}:</label>
                <br> <!-- 添加换行 -->
                ${generateMatrixInput(rows, cols, matrixId)} <!-- 显示矩阵输入 -->
            </div>
            <button type="button" onclick="deleteMatrix('${matrixId}', secondaryMatrices)">删除矩阵</button>
        </div>
    `;

    document.getElementById("secondary-matrices-container").insertAdjacentHTML("beforeend", matrixHTML);

    // 存储矩阵信息
    secondaryMatrices.push({ id: matrixId, rows, cols });
}
//支持分数输入
function validateInput(inputId) {
    const inputElement = document.getElementById(inputId);
    let inputValue = inputElement.value.trim();

    // 如果是分数格式，如 "3/4"
    if (/^\d+\/\d+$/.test(inputValue)) {
        const [numerator, denominator] = inputValue.split('/').map(Number);
        if (denominator === 0) {
            alert("分母不能为零！");
            inputElement.value = '';
            return;
        }
        // 将分数转为小数
        inputValue = numerator / denominator;
    }

    // 检查是否是有效的数字
    const parsedValue = parseFloat(inputValue);
    if (isNaN(parsedValue)) {
        alert("请输入有效的数字或分数！");
        inputElement.value = '';
    } else {
        inputElement.value = parsedValue;  // 如果是有效的数字或分数，将其转为小数
    }
}

// 生成矩阵输入框的函数
function generateMatrixInput(rows, cols, matrixId) {
    let html = "";
    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            html += `<input type="text" id="${matrixId}-${i}-${j}" placeholder="[${i}][${j}]" onblur="validateInput('${matrixId}-${i}-${j}')">`;
        }
        html += "<br>";
    }
    return html;
}

// 删除矩阵的函数
function deleteMatrix(matrixId, matrixArray) {
    // 从页面中移除矩阵
    const matrixElement = document.getElementById(matrixId);
    if (matrixElement) {
        matrixElement.remove();
    }

    // 从存储中移除矩阵信息
    const index = matrixArray.findIndex(matrix => matrix.id === matrixId);
    if (index !== -1) {
        matrixArray.splice(index, 1); // 删除指定矩阵
    }
}

// 获取所有矩阵数据的函数
function getAllMatrixValues(matrixArray) {
    const result = {};
    matrixArray.forEach(matrix => {
        const { id, rows, cols } = matrix;
        const values = [];
        for (let i = 0; i < rows; i++) {
            const row = [];
            for (let j = 0; j < cols; j++) {
                const inputValue = document.getElementById(`${id}-${i}-${j}`).value.trim();

                let value = parseFloat(inputValue); // 默认尝试转为浮点数
                // 如果是分数，则处理
                if (/^\d+\/\d+$/.test(inputValue)) {
                    const [numerator, denominator] = inputValue.split('/').map(Number);
                    if (denominator !== 0) {
                        value = numerator / denominator;
                    } else {
                        value = 0;  // 防止分母为零
                    }
                }

                row.push(value || 0);  // 确保有值
            }
            values.push(row);
        }
        result[id] = values;
    });
    return result;
}

// 创建模糊评价矩阵
function createSecondaryMatrices() {
    secondaryMatrices.forEach(matrix => {
        const cols = 5; // 行数固定为5
        const rows = matrix.rows; // 列数使用矩阵的行数（由于是方阵）

        // 生成唯一的模糊评价矩阵 ID
        const matrixId = `fuzzy-evaluation-matrix-${Fuzzy_Evaluation_MatrixCounter++}`;

        // 创建矩阵的 HTML
        const matrixHTML = `
            <div class="matrix-container" id="${matrixId}">
                <div class="matrix-input">
                    <label>模糊评价矩阵 ${matrixId}:</label>
                <br> <!-- 添加换行 -->
                ${generateMatrixInput(rows, cols, matrixId)} <!-- 显示矩阵输入 -->
                </div>
                <button type="button" onclick="deleteMatrix('${matrixId}', fuzzyevaluationMatrices)">删除矩阵</button>
            </div>
        `;

        // 将矩阵添加到页面中
        document.getElementById("fuzzy-evaluation-matrices").insertAdjacentHTML("beforeend", matrixHTML);

        // 存储矩阵信息
        fuzzyevaluationMatrices.push({ id: matrixId, rows, cols });
    });
}

// 表单提交事件
document.getElementById("matrix-form").addEventListener("submit", function (event) {
    event.preventDefault();

    // 获取所有一级指标和二级指标矩阵的值
    const primaryMatrixValues = getAllMatrixValues(primaryMatrices);
    const secondaryMatrixValues = getAllMatrixValues(secondaryMatrices);
    const fuzzyevaluationMatrixValues = getAllMatrixValues(fuzzyevaluationMatrices);
    console.log("一级指标矩阵的值:", primaryMatrixValues);
    console.log("二级指标矩阵的值:", secondaryMatrixValues);
    console.log("模糊矩阵的值:", fuzzyevaluationMatrixValues);

    // 调用后端计算逻辑
    fetch("/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            primaryMatrices: primaryMatrixValues,
            secondaryMatrices: secondaryMatrixValues,
            fuzzyevaluationMatrices:fuzzyevaluationMatrixValues,
            score_standard: [100, 80, 60, 40, 0],
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("result").innerHTML = `
                <p>综合得分：${data.final_score}</p>
                <br>
                <p>每一个一级指标下二级指标得分：<br>${data.All_primary_score}</p>
                <br>
                <p>每个一级指标下二级指标各项得分：<br>${data.All_secondary_score}</p>
            `;
        })
        .catch((error) => {
            console.error("计算失败：", error);
        });
});