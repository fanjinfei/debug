<template>
  <div id="app">
    <h1>Hello World !</h1>
    <div class="full-width center-content">
      <hello name="World2" />
    </div>
    <ol>
        <todo-item
          v-for="item in groceryList"
          v-bind:todo="item"
          v-bind:key="item.id"
        ></todo-item>
    </ol>
  </div>
</template>

<script>
import Hello from '../components/Hello.vue'
export default {
  name: "App",
  components: {
    Hello
  },
  data() {
    return {
        groceryList: [
          { id: 0, text: 'Vegetables' },
          { id: 1, text: 'Cheese' },
          { id: 2, text: 'Whatever else humans are supposed to eat' }
        ]
   };
 }

}
</script>

