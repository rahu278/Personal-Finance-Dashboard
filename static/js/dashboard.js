// ======================================
// PERSONAL FINANCE DASHBOARD
// ======================================

document.addEventListener("DOMContentLoaded", function () {
    loadExpenseChart();
    loadMonthlyChart();
});


// ======================================
// EXPENSE CATEGORY CHART
// ======================================

async function loadExpenseChart() {
    try {
        const response = await fetch("/api/expense_categories");

        if (!response.ok) {
            throw new Error("Expense API failed");
        }

        const data = await response.json();

        const canvas = document.getElementById("expenseChart");
        const legend = document.getElementById("expenseLegend");

        if (!canvas) return;

        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (!data || data.length === 0) {
            ctx.font = "18px Arial";
            ctx.textAlign = "center";
            ctx.fillStyle = "#555";

            ctx.fillText(
                "No expense data available",
                canvas.width / 2,
                canvas.height / 2
            );

            if (legend) {
                legend.innerHTML = "";
            }

            return;
        }

        drawPieChart(ctx, canvas, data);
        createExpenseLegend(legend, data);

    } catch (error) {
        console.error("Expense chart error:", error);
    }
}


// ======================================
// PIE CHART
// ======================================

function drawPieChart(ctx, canvas, data) {

    const total = data.reduce(function (sum, item) {
        return sum + Number(item.total);
    }, 0);

    if (total <= 0) {
        return;
    }

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    const radius = Math.min(centerX, centerY) - 35;

    let startAngle = 0;

    data.forEach(function (item, index) {

        const value = Number(item.total);

        const sliceAngle =
            (value / total) * Math.PI * 2;

        const endAngle =
            startAngle + sliceAngle;

        ctx.beginPath();

        ctx.moveTo(centerX, centerY);

        ctx.arc(
            centerX,
            centerY,
            radius,
            startAngle,
            endAngle
        );

        ctx.closePath();

        ctx.fillStyle = getChartColor(index);

        ctx.fill();

        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;

        ctx.stroke();

        startAngle = endAngle;
    });
}


// ======================================
// EXPENSE LEGEND
// ======================================

function createExpenseLegend(legend, data) {

    if (!legend) return;

    legend.innerHTML = "";

    const total = data.reduce(function (sum, item) {
        return sum + Number(item.total);
    }, 0);

    data.forEach(function (item, index) {

        const percentage =
            (
                Number(item.total) /
                total *
                100
            ).toFixed(1);

        const div = document.createElement("div");

        div.className = "legend-item";

        const color = document.createElement("span");

        color.className = "legend-color";

        color.style.backgroundColor =
            getChartColor(index);

        const text = document.createElement("span");

        text.innerText =
            item.name +
            " - ₹" +
            Number(item.total).toFixed(2) +
            " (" +
            percentage +
            "%)";

        div.appendChild(color);
        div.appendChild(text);

        legend.appendChild(div);
    });
}


// ======================================
// MONTHLY CHART
// ======================================

async function loadMonthlyChart() {

    try {

        const response =
            await fetch("/api/monthly");

        if (!response.ok) {
            throw new Error("Monthly API failed");
        }

        const data =
            await response.json();

        const canvas =
            document.getElementById("monthlyChart");

        if (!canvas) return;

        const ctx =
            canvas.getContext("2d");

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        // Convert object into array
        const chartData =
            Object.keys(data).map(function (month) {

                return {
                    month: month,
                    income: Number(data[month].Income || 0),
                    expense: Number(data[month].Expense || 0)
                };

            });

        if (chartData.length === 0) {

            ctx.font = "18px Arial";
            ctx.textAlign = "center";
            ctx.fillStyle = "#555";

            ctx.fillText(
                "No monthly data available",
                canvas.width / 2,
                canvas.height / 2
            );

            return;
        }

        drawMonthlyBarChart(
            ctx,
            canvas,
            chartData
        );

    } catch (error) {

        console.error(
            "Monthly chart error:",
            error
        );

    }
}


// ======================================
// MONTHLY BAR CHART
// ======================================

function drawMonthlyBarChart(
    ctx,
    canvas,
    data
) {

    const padding = 55;

    const chartWidth =
        canvas.width - padding * 2;

    const chartHeight =
        canvas.height - padding * 2;

    let maximum = 0;

    data.forEach(function (item) {

        maximum =
            Math.max(
                maximum,
                Number(item.income),
                Number(item.expense)
            );

    });

    if (maximum === 0) {
        maximum = 100;
    }

    // AXIS

    ctx.beginPath();

    ctx.moveTo(
        padding,
        padding
    );

    ctx.lineTo(
        padding,
        canvas.height - padding
    );

    ctx.lineTo(
        canvas.width - padding,
        canvas.height - padding
    );

    ctx.strokeStyle = "#777";

    ctx.lineWidth = 1;

    ctx.stroke();


    const groupWidth =
        chartWidth / data.length;

    const barWidth =
        Math.min(
            22,
            groupWidth / 3
        );


    data.forEach(function (item, index) {

        const x =
            padding +
            groupWidth * index +
            groupWidth / 2;


        const income =
            Number(item.income);

        const expense =
            Number(item.expense);


        const incomeHeight =
            (income / maximum) *
            chartHeight;

        const expenseHeight =
            (expense / maximum) *
            chartHeight;


        // INCOME

        ctx.fillStyle = "#16a34a";

        ctx.fillRect(
            x - barWidth - 2,
            canvas.height -
                padding -
                incomeHeight,
            barWidth,
            incomeHeight
        );


        // EXPENSE

        ctx.fillStyle = "#dc2626";

        ctx.fillRect(
            x + 2,
            canvas.height -
                padding -
                expenseHeight,
            barWidth,
            expenseHeight
        );


        // MONTH

        ctx.fillStyle = "#333";

        ctx.font = "12px Arial";

        ctx.textAlign = "center";

        ctx.fillText(
            formatMonth(item.month),
            x,
            canvas.height -
                padding +
                20
        );

    });


    // LEGEND

    ctx.font = "12px Arial";

    ctx.textAlign = "left";


    ctx.fillStyle = "#16a34a";

    ctx.fillRect(
        canvas.width - 155,
        15,
        12,
        12
    );

    ctx.fillStyle = "#333";

    ctx.fillText(
        "Income",
        canvas.width - 138,
        25
    );


    ctx.fillStyle = "#dc2626";

    ctx.fillRect(
        canvas.width - 85,
        15,
        12,
        12
    );

    ctx.fillStyle = "#333";

    ctx.fillText(
        "Expense",
        canvas.width - 68,
        25
    );
}


// ======================================
// FORMAT MONTH
// ======================================

function formatMonth(month) {

    if (!month) return "";

    const parts =
        month.split("-");

    if (parts.length !== 2) {
        return month;
    }

    const year = parts[0];

    const monthNumber =
        Number(parts[1]);

    const names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
    ];

    return (
        names[monthNumber - 1] +
        " " +
        year
    );
}


// ======================================
// CHART COLORS
// ======================================

function getChartColor(index) {

    const colors = [
        "#2563eb",
        "#16a34a",
        "#dc2626",
        "#f59e0b",
        "#7c3aed",
        "#0891b2",
        "#db2777",
        "#65a30d",
        "#ea580c",
        "#4f46e5"
    ];

    return colors[
        index % colors.length
    ];
}