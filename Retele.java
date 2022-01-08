import java.io.IOException;

class Retele {
    public static void main(String[] args) throws IOException, InterruptedException {
        Task1 task1 = new Task1();
        task1.readProblemData();
        task1.formulateOracleQuestion();
        task1.askOracle();

    }
}