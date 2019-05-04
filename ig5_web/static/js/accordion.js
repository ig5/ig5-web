function toggle(id,text){
  var ele = document.getElementById(id);
  if (!ele) {
    return;
  }
  var text = document.getElementById(text);
  if(ele.style.display == "none") {
        ele.style.display = "block";
    text.innerHTML = "Skryť zoznam otázok a úloh &laquo;";
    }
  else {
    ele.style.display = "none";
    text.innerHTML = "Zobraziť zoznam otázok a úloh &raquo;";
  }
}
