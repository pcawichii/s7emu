$(document).ready(() => {
  $("#power_2").hide()
  $("#power_2").load("/selenium", ()=>{
    $("#power_2").show()
    $("#power_1").hide()
  })
})
