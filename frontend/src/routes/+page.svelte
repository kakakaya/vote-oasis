<script>
    let question = "今日の気分は？";
    let answer = "";

    function submitAnswer() {
        alert(`回答: ${answer}`);
        answer = "";
    }
</script>

<h1>アンケート</h1>
<p>{question}</p>
<input bind:value={answer} placeholder="回答を入力" />
<button on:click={submitAnswer}>送信</button>
