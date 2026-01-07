<script setup>
  import { computed, ref } from 'vue'

  const colorSet1 = [
    ["#e91e63", "#4caf50",],
    ["#ff5252", "#26a69a",],
    ["#ff6d00", "#00bcd4",],
    ["#ffb74d", "#2196f3",],
    ["#fdd835", "#7e57c2",],
    ["#cddc39", "#9c27b0",],
  ]
  const colorSet2 = [
    ["#ff0000", "#ff8700", "#ffd300", "#deff0a", "#a1ff0a", "#0aff99"],
    ["#0aefff", "#147df5", "#580aff", "#be0aff"],
  ]
  const colorSet3 = [
    ["#33a8c7", "#52e3e1", "#a0e426", "#fdf148", "#ffab00", "#f77976"],
    ["#f050ae", "#d883ff", "#9336fd"],
  ]
  const colorSet4 = [
    ["#e63232", "#f3722c", "#f8961e", "#ffd043", "#7fc96b", "#43aa8b"],
    ["#277da1", "#3b498e", "#66418a"],
  ]

  const props = defineProps({
    index: {
      type: Number,
      default: null
    },
    cobo: {
      type: String,
      default: ""
    },
    asad: {
      type: String,
      default: ""
    },
    aget: {
      type: String,
      default: ""
    },
    channel: {
      type: String,
      default: ""
    },
    color: {
      type: String,
      default: "#E91E63"
    }
  })

  // input rules
  const rules = {
    required: value => !!value || "Required",
    digits: value => {
      const pattern = /^[0-9]+|\*$/
      return pattern.test(value) || "Must be digits"
    },
    cobo: value =>
      value == "*"
      || (Number(value) >= 0 && Number(value) < 11)
      || 'Cobo must be between 0 and 10',
    asad: value =>
      value == "*"
      || (Number(value) >= 0 && Number(value) < 4)
      || 'Asad must be between 0 and 3',
    aget: value =>
      value == "*"
      || (Number(value) >= 0 && Number(value) < 4)
      || 'Aget must be between 0 and 3',
    channel: value =>
      value == "*"
      || (
        Number(value) >= 0
        && Number(value) < 68
        && Number(value) != 11
        && Number(value) != 22
        && Number(value) != 45
        && Number(value) != 56
      )
      || 'Channel must be between 0 and 67, and not be 11, 22, 45 or 56',
    hexColor: value => {
      const pattern = /^#?[0-9a-fA-F]{6}$/
      return pattern.test(value) || "Must be a valid hex color"
    }
  }
  // AGET hardware ID
  const cobo = ref(props.cobo)
  const asad = ref(props.asad)
  const aget = ref(props.aget)
  const channel = ref(props.channel)

  // select color
  const rawSelectedColor = ref(props.color)
  const selectedColor = computed({
    get() {
      return rawSelectedColor.value
    },
    set(value) {
      if (value.slice(0, 1) != "#") {
        value = "#" + value
      }
      value = value.toUpperCase()
      rawSelectedColor.value = value
    }
  })

  // color swatcher
  const showColorSwatcher = ref(true)

  // more color picker
  const showMoreColorPicker = ref(false)

  const form = ref()

  const emit = defineEmits(["apply"])
  async function apply() {
    const { valid } = await form.value.validate()
    if (!valid) return
    emit(
      "apply",
      props.index,
      cobo.value, asad.value, aget.value, channel.value,
      selectedColor.value
    )
  }
</script>


<template>
  <v-card min-width="400">
    <v-card-title>Render conditions</v-card-title>
    <v-container>
      <v-form ref="form">
        <v-row>
          <v-col>
            <v-text-field
              v-model="cobo"
              label="Cobo"
              :rules="[rules.required, rules.digits, rules.cobo]"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              v-model="asad"
              label="Asad"
              :rules="[rules.required, rules.digits, rules.asad]"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="aget"
              label="Aget"
              :rules="[rules.required, rules.digits, rules.aget]"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              v-model="channel"
              label="Channel"
              :rules="[rules.required, rules.digits, rules.channel]"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="selectedColor"
              :rules="[rules.hexColor]"
            >
              <template v-slot:prepend>
                Color
              </template>
              <template v-slot:append>
                <v-btn
                  variant="flat"
                  :color="selectedColor"
                  @click="showColorSwatcher = !showColorSwatcher"
                ></v-btn>
              </template>
            </v-text-field>
          </v-col>
        </v-row>
        <v-expand-transition>
          <v-card v-show="showColorSwatcher">
            <v-color-picker
              v-model="rawSelectedColor"
              mode="hex"
              hide-inputs
              :hide-canvas="!showMoreColorPicker"
              :hide-sliders="!showMoreColorPicker"
              show-swatches
              :swatches="colorSet1"
              elevation="0"
              width="350"
            >
            </v-color-picker>
            <v-btn variant="text" @click="showMoreColorPicker = !showMoreColorPicker">
              <span v-if="!showMoreColorPicker">More colors</span>
              <span v-else>Less colors</span>
            </v-btn>
          </v-card>
        </v-expand-transition>
      </v-form>
    </v-container>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        text="Apply"
        @click="apply"
      />
    </v-card-actions>
  </v-card>
</template>