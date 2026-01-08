<script setup>
  import { ref, reactive, defineAsyncComponent } from 'vue'

  const PixiCanvas = defineAsyncComponent(() => import('./components/PixiCanvas.vue'))
  const RenderColorMenu = defineAsyncComponent(() => import('./components/RenderColorMenu.vue'))

  // rendered pads/strips
  const rendered = reactive([])
  function addRendered(cobo, asad, aget, channel, color) {
    rendered.push({
      cobo: cobo,
      asad: asad,
      aget: aget,
      channel: channel,
      color: color
    })
  }
  function removeRendered(index) {
    rendered.splice(index, 1)
  }

  // show render color menu
  const showRenderColorMenu = ref(false)
  const renderMenuArgs = ref(null)
  const renderColorMenuTarget = ref(null)

  async function clickRenderColorMenu(evt, args, index) {
    if (showRenderColorMenu.value) {
      showRenderColorMenu.value = false
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    if (!args) {
      renderMenuArgs.value = {
        index: undefined,
        cobo: undefined,
        asad: undefined,
        aget: undefined,
        channel: undefined,
        color: undefined
      }
    } else {
      renderMenuArgs.value = {
        index: index,
        cobo: args.cobo,
        asad: args.asad,
        aget: args.aget,
        channel: args.channel,
        color: args.color
      }
    }
    renderColorMenuTarget.value = evt.target.closest('.v-btn')
    showRenderColorMenu.value = true
  }

  function applyRenderColor(index, cobo, asad, aget, channel, color) {
    showRenderColorMenu.value = false
    if (index === null) {
      addRendered(cobo, asad, aget, channel, color)
    } else {
      rendered[index] = {
        cobo: cobo,
        asad: asad,
        aget: aget,
        channel: channel,
        color: color
      }
    }
  }

  // select layer
  const layers = ["Pads", "Si-0", "Si-1"]
  const selectedLayer = ref(layers[0])

  // select view
  const views = ["Upstream", "Downstream"]
  const selectedView = ref(views[0])

</script>


<template>
  <v-app>
    <v-navigation-drawer permanent width=400>
      <v-list class="mt-2">
        <v-list-item>
          <template v-slot:prepend>
            <v-avatar color="white"></v-avatar>
          </template>
          <template v-slot:subtitle>
            <v-row>
              <v-col cols="3">Cobo</v-col>
              <v-col cols="3">Asad</v-col>
              <v-col cols="3">Aget</v-col>
              <v-col cols="3">Ch</v-col>
            </v-row>
          </template>
          <template v-slot:append>
            <v-btn variant="plain" density="compact" disabled icon=""></v-btn>
            <v-btn variant="plain" density="compact" disabled icon=""></v-btn>
          </template>
        </v-list-item>
        <v-list-item
          v-for="(item, index) in rendered"
        >
          <template v-slot:prepend>
            <v-avatar :color="item.color"/>
          </template>
          <template v-slot:title>
            <v-row>
              <v-col cols="3">{{ item.cobo }}</v-col>
              <v-col cols="3">{{ item.asad }}</v-col>
              <v-col cols="3">{{ item.aget }}</v-col>
              <v-col cols="3">{{ item.channel }}</v-col>
            </v-row>
          </template>
          <template v-slot:append>
            <v-btn
              variant="plain"
              icon="mdi-pencil"
              density="compact"
              @click="clickRenderColorMenu($event, item, index)"
            ></v-btn>
            <v-btn
              variant="plain"
              icon="mdi-delete"
              density="compact"
              @click="removeRendered(index)"
            ></v-btn>
          </template>
        </v-list-item>
        <v-list-item>
          <v-btn
            block border="dashed thin"
            rounded="lg"
            elevation="0"
            @click="clickRenderColorMenu($event, null, null)"
            text="New"
          />
        </v-list-item>
      </v-list>

      <v-menu
        v-model="showRenderColorMenu"
        :close-on-content-click="false"
        :target="renderColorMenuTarget"
        location="end"
      >
        <RenderColorMenu
          :index="renderMenuArgs.index"
          :cobo="renderMenuArgs.cobo"
          :asad="renderMenuArgs.asad"
          :aget="renderMenuArgs.aget"
          :channel="renderMenuArgs.channel"
          :color="renderMenuArgs.color"
          :key="showRenderColorMenu"
          @apply="applyRenderColor"
        />
      </v-menu>
    </v-navigation-drawer>
    <v-main>
      <v-row justify="center" class="mt-8">
        <v-col cols="4" class="d-flex justify-center">
          <v-btn-toggle
            v-model="selectedLayer"
            color="primary"
            group
            mandatory
            divided
            border="solid thin"
            rounded="lg"
          >
            <v-btn
              v-for = "layer in layers"
              :key="layer"
              :value="layer"
              class="text-none"
            >{{ layer }}</v-btn>
          </v-btn-toggle>
        </v-col>
        <v-col cols="4" class="d-flex justify-center">
          <v-btn-toggle
            v-model="selectedView"
            color="primary"
            group
            mandatory
            divided
            border="solid thin"
            rounded="lg"
          >
            <v-btn
              v-for = "view in views"
              :key="view"
              :value="view"
              class="text-none"
            >{{ view }}</v-btn>
          </v-btn-toggle>
        </v-col>
      </v-row>
      <PixiCanvas
        :rendered="rendered"
        :view="selectedView"
      />
    </v-main>
  </v-app>
</template>
