<script setup>
  import { onUnmounted, onMounted, ref, computed, watch } from "vue"
  import { Application, Container, FillGradient, Graphics, Point, RenderLayer } from "pixi.js"

  const props = defineProps({
    rendered: {
      type: Array,
      default: [],
    },
    view: {
      type: String,
      required: true,
    }
  })

  const canvas = ref(null)

  const selectedPad = ref(null)
  const savePad = {
    points: null,
    color: null,
    position: null,
    scale: null,
  }
  const floatLayer = new RenderLayer()
  const selectedPadIndex = computed(() => selectedPad.value?.index ?? "")
  const selectedPadCobo = computed(() => selectedPad.value?.cobo ?? "")
  const selectedPadAsad = computed(() => selectedPad.value?.asad ?? "")
  const selectedPadAget = computed(() => selectedPad.value?.aget ?? "")
  const selectedPadChannel = computed(() => selectedPad.value?.channel ?? "")

  const mouseX = ref(0)
  const mouseY = ref(0)
  let lastClickSelect = false
  const initXScale = 1.3
  const initYScale = -1.3
  let zoomScale = 1
  let revertX = props.view == "Upstream" ? -1 : 1
  let revertY = 1

  let container
  let onMouseDown
  let onMouseUp
  let onMouseMove
  let onMouseLeave
  let onWheel
  let isDragging = false
  let dragged = false
  let dragStart = { x: 0, y: 0 }
  let containerStart = { x: 0, y: 0 }

  // for render pads
  const floatScale = 1.3
  const half_edge = 4.5
  const height = half_edge * (3**0.5)
  const half_height = height * 0.5
  const defaultColor = 0xc0c0c0
  // const selectedColor = new FillGradient({
  //   colorStops: [
  //     { offset: 0, color: "#d883ff" },
  //     { offset: 1, color: "#52e3e1" },
  //   ]
  // })
  const selectedColor = "#000000"
  const pads = []

  function restorePad(pad, from) {
    floatLayer.detachAll()
    pad.clear()
    pad.poly(from.points)
    pad.fill(from.color)
    pad.x = from.position.x
    pad.y = from.position.y
    pad.scale = from.scale
  }

  function getRenderColor(padData, rendered) {
    for (let item of rendered) {
      if (item.cobo != padData.cobo && item.cobo != "*") continue
      if (item.asad != padData.asad && item.asad != "*") continue
      if (item.aget != padData.aget && item.aget != "*") continue
      if (item.channel != padData.channel && item.channel != "*") continue
      return item.color
    }
    return defaultColor
  }

  function getPadOrthoPoints(direction) {
    return direction == 0
      ? [-half_height,-half_edge, -half_height, half_edge, half_height,0.0]
      : [half_height,-half_edge, half_height,half_edge, -half_height,0.0]
  }

  function getPadPoints(direction) {
    return direction == 1
      ? [-height/3,-half_edge, -height/3,half_edge, height*2/3,0.0]
      : [height/3,-half_edge, height/3,half_edge, -height*2/3,0.0]
  }

  function getPadOrthoPosition(padData) {
    return {
      x: padData.cx,
      y: padData.cy,
    }
  }

  function getPadPosition(padData) {
    return {
      x: padData.cx,
      y: padData.cy,
    }
  }

  function initPad(pad, padData) {
    pad.poly(padData.points)
    pad.fill(padData.color)
    pad.x = padData.position.x
    pad.y = padData.position.y
    pad.scale = padData.scale
  }

  async function drawPads(container) {
    const padData = await (await fetch("/map/pads.json")).json()
    for (let i = 0; i < padData.length; i++) {
      const pad = new Graphics()
      initPad(pad, {
        points: getPadPoints(padData[i].direction),
        color: getRenderColor(padData[i], props.rendered),
        position: getPadPosition(padData[i]),
        scale: padData[i].scale,
      })
      pad.interactive = true
      pad.cursor = "pointer"
      pad.on("mouseenter", (evt) => {
        pad.scale.set(padData[i].scale*floatScale)
      })
      pad.on("mouseleave", (evt) => {
        if (selectedPad.value == null || selectedPad.value.index != i) {
          pad.scale.set(padData[i].scale)
        }
      })
      pad.on("click", (evt) => {
        if (dragged) return
        lastClickSelect = true
        if (!!selectedPad.value) {
          restorePad(selectedPad.value.pad, savePad)
        }
        selectedPad.value = {
          index: i,
          cobo: padData[i].cobo,
          asad: padData[i].asad,
          aget: padData[i].aget,
          channel: padData[i].channel,
          pad: pad,
        }
        savePad.points = getPadPoints(padData[i].direction)
        savePad.color = getRenderColor(padData[i], props.rendered)
        savePad.position = getPadPosition(padData[i])
        savePad.scale = padData[i].scale
        pad.clear()
        initPad(pad, {
          points: getPadPoints(padData[i].direction),
          color: selectedColor,
          position: getPadPosition(padData[i]),
          scale: padData[i].scale*floatScale,
        })
        floatLayer.attach(pad)
      })
      container.addChild(pad)
      pads.push(pad)
    }
  }

  onMounted(async () => {
    const app = new Application()
    await app.init({
      background: "#ffffff",
      resizeTo: canvas.value,
      antialias: true,
    })
    canvas.value.appendChild(app.canvas)
    container = new Container()
    app.stage.addChild(container)

    await drawPads(container)
    app.stage.addChild(floatLayer)

    container.x = app.screen.width / 2
    container.y = app.screen.height / 2
    container.scale.x = initXScale * zoomScale * revertX
    container.scale.y = initYScale * zoomScale * revertY

    function getClipXY(evt) {
      const rect = app.canvas.getBoundingClientRect()
      const x = (evt.clientX - rect.left) * (app.renderer.width / rect.width)
      const y = (evt.clientY - rect.top) * (app.renderer.height / rect.height)
      return { x, y }
    }

    onMouseDown = (evt) => {
      isDragging = true
      dragged = false
      const {x, y} = getClipXY(evt)
      dragStart = { x: x, y: y }
      containerStart = { x: container.x, y: container.y}
    }

    onMouseMove = (evt) => {
      const { x, y } = getClipXY(evt)
      const worldPos = container.toLocal(new Point(x, y))
      mouseX.value = worldPos.x
      mouseY.value = worldPos.y

      if (isDragging) {
        dragged = true
        container.x = containerStart.x + (x - dragStart.x)
        container.y = containerStart.y + (y - dragStart.y)
      }
    }

    onMouseUp = () => {
      isDragging = false
      if (lastClickSelect) {
        lastClickSelect = false
      } else if (!dragged) {
        if (selectedPad.value) {
          restorePad(selectedPad.value.pad, savePad)
          selectedPad.value = null
        }
      }
    }

    onMouseLeave = () => {
      isDragging = false
    }

    onWheel = (evt) => {
      evt.preventDefault()
      const {x, y} = getClipXY(evt)
      const mouseWorldBefore = container.toLocal(new Point(x, y))
      const zoomFactor = evt.deltaY < 0 ? 1.1 : 1/1.1
      zoomScale *= zoomFactor
      zoomScale = Math.min(Math.max(zoomScale, 0.8), 12)
      container.scale.x = initXScale * zoomScale * revertX
      container.scale.y = initYScale * zoomScale * revertY
      const mouseWorldAfter = container.toLocal(new Point(x, y))
      container.x += (mouseWorldAfter.x - mouseWorldBefore.x) * initXScale*zoomScale*revertX
      container.y += (mouseWorldAfter.y - mouseWorldBefore.y) * initYScale*zoomScale*revertY
    }

    canvas.value.addEventListener("mousedown", onMouseDown)
    canvas.value.addEventListener("mouseup", onMouseUp)
    canvas.value.addEventListener("mousemove", onMouseMove)
    canvas.value.addEventListener("mouseleave", onMouseLeave)
    canvas.value.addEventListener("wheel", onWheel)
  })

  onUnmounted(() => {
    if (canvas.value) {
      canvas.value.removeEventListener("mousedown", onMouseDown)
      canvas.value.removeEventListener("mouseup", onMouseUp)
      canvas.value.removeEventListener("mousemove", onMouseMove)
      canvas.value.removeEventListener("mouseleave", onMouseLeave)
      canvas.value.removeEventListener("wheel", onWheel)
    }
    app.destroy(true)
  })

  let oldRendered = [...props.rendered]
  watch(props.rendered, async (newRendered) => {
    const padData = await (await fetch("/map/pads.json")).json()
    for (let i = 0; i < pads.length; i++) {
      let oldColor = getRenderColor(padData[i], oldRendered)
      let newColor = getRenderColor(padData[i], newRendered)
      if (oldColor == newColor) continue
      pads[i].clear()
      initPad(pads[i], {
        points: getPadPoints(padData[i].direction),
        color: newColor,
        position: getPadPosition(padData[i]),
        scale: pads[i].scale.x,
      })
    }
    if (!!selectedPad.value) {
      selectedPad.value.pad.clear()
      initPad(selectedPad.value.pad, {
        points: getPadPoints(padData[selectedPad.value.index].direction),
        color: selectedColor,
        position: getPadPosition(padData[selectedPad.value.index]),
        scale: padData[selectedPad.value.index].scale*floatScale,
      })
      savePad.color = getRenderColor(padData[selectedPad.value.index], newRendered)
    }
    oldRendered = [...props.rendered]
  })

  watch(() => props.view, (newView) => {
    console.log(newView == "Upstream")
    if (newView == "Upstream") {
      revertX = -1
    } else {
      revertX = 1
    }
    container.scale.x = initXScale * zoomScale * revertX
    container.scale.y = initYScale * zoomScale * revertY
  })

</script>

<template>
  <v-row>
    <v-col cols="6" offset="3" class="d-flex justify-center mt-2">
      <p v-show="selectedPad">
        Selected:
        Cobo {{ selectedPadCobo }},
        Asad {{ selectedPadAsad }},
        Aget {{ selectedPadAget }},
        Channel {{ selectedPadChannel }},
        Pad {{ selectedPadIndex }}
      </p>
      <p v-show="!selectedPad" style="visibility: hidden">_</p>
    </v-col>
  </v-row>
  <div ref="canvas" class="pixi-root"></div>
  <v-row>
    <v-col cols="6" offset="3" class="d-flex justify-center">
      <p>
        x: {{ mouseX.toFixed(2) }} mm, y: {{ mouseY.toFixed(2) }} mm
        <v-tooltip text="In fixed global coordinate system.">
          <template v-slot:activator="{ props: activatorProps }">
            <v-btn
              variant="icon"
              icon="mdi-information-outline"
              v-bind="activatorProps"
            />
          </template>
        </v-tooltip>
      </p>
    </v-col>
  </v-row>
</template>

<style scoped>
.pixi-root {
  height: 80vh;
  overflow: hidden;
  border: solid thin #c0c0c0;
}
</style>
