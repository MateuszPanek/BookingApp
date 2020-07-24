function dayChoices(availability, month) {
    var days = availability[month];
    alert(days);
    return days;

}

function displayDays(){
    let i = 0;
    let month = document.getElementById('id_month').value;
    let day = document.getElementById('id_day');
    for(let d in data_from_django[month]) {
        day.options[i] = new Option(d, d)
        i ++
    }
}

