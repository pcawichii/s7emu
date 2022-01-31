$(document).ready(() => {
  $("#power_2").hide()
  $("#power_2").load("/selenium", () => {
    $("#power_2").show()
    $("#power_1").hide()
  })
  $("#stat_2").load("/status_gen", () => {
    $("#stat_2").show()
    $("#stat_1").hide()
  })
})
