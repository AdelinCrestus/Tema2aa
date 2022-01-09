import java.io.*;
import java.util.ArrayList;
import java.util.Comparator;

public class Task2 extends Task {
    private int N, M, K;
    private ArrayList<Muchie> muchii;
    private int[][] matAdiacenta;
    private int[][] x;
    private int numarulVariabilelor;
    private  boolean solutie;
    private ArrayList<Integer> variabile = new ArrayList<>();
    private ArrayList<Integer> persoane = new ArrayList<>();

    public int getK() {
        return K;
    }

    public void setK(int k) {
        K = k;
    }

    public int getN() {
        return N;
    }

    public void setN(int n) {
        N = n;
    }

    public int getM() {
        return M;
    }

    public void setM(int m) {
        M = m;
    }

    public ArrayList<Muchie> getMuchii() {
        return muchii;
    }

    public void setMuchii(ArrayList<Muchie> muchii) {
        this.muchii = muchii;
    }

    public int[][] getMatAdiacenta() {
        return matAdiacenta;
    }

    public void setMatAdiacenta(int[][] matAdiacenta) {
        this.matAdiacenta = matAdiacenta;
    }

    public int[][] getX() {
        return x;
    }

    public void setX(int[][] x) {
        this.x = x;
    }

    public int getNumarulVariabilelor() {
        return numarulVariabilelor;
    }

    public void setNumarulVariabilelor(int numarulVariabilelor) {
        this.numarulVariabilelor = numarulVariabilelor;
    }

    public boolean isSolutie() {
        return solutie;
    }

    public void setSolutie(boolean solutie) {
        this.solutie = solutie;
    }

    public ArrayList<Integer> getVariabile() {
        return variabile;
    }

    public void setVariabile(ArrayList<Integer> variabile) {
        this.variabile = variabile;
    }

    public ArrayList<Integer> getPersoane() {
        return persoane;
    }

    public void setPersoane(ArrayList<Integer> persoane) {
        this.persoane = persoane;
    }

    @Override
    public void solve() throws IOException, InterruptedException {
        readProblemData();
        setK(1);
        while (!solutie) {
            formulateOracleQuestion();
            askOracle();
            decipherOracleAnswer();
            setK(getK() + 1);
        }
        writeAnswer();
    }

    @Override
    public void readProblemData() throws IOException {
        InputStreamReader inputStreamReader = new InputStreamReader(System.in);
        BufferedReader input = new BufferedReader(inputStreamReader);
        String input_String;
        input_String= input.readLine();
        int i = 0;
        for (String val: input_String.split(" ")) {

            switch (i) {
                case 0 -> {
                    N = Integer.parseInt(val);
                }
                case 1 -> {
                    M = Integer.parseInt(val);
                }
            }
            i++;
        }

        for( i = 0 ; i < M ; i++) {
            input_String = input.readLine();
            Muchie muc = new Muchie();
            int j = 0;
            for( String val : input_String.split( " ")) {
                switch (j) {
                    case 0 -> {
                        muc.setA(Integer.parseInt(val));
                    }
                    case 1 -> {
                        muc.setB(Integer.parseInt(val));
                    }
                }
                j++;
            }
            if( muchii == null) {
                muchii = new ArrayList<>();
            }
            muchii.add(muc);
        }

        matAdiacenta = new int[N+1][N+1];
        for(Muchie muchie : muchii ) {
            matAdiacenta[muchie.getA()][muchie.getB()] = 1;
            matAdiacenta[muchie.getB()][muchie.getA()] = 1;
        }

    }

    @Override
    public void formulateOracleQuestion() throws IOException {
        x = new int[K+1][N+1];
        int numaratoare = 1, i;
        for (i = 1 ; i <= K ; i++) {
            for (int j = 1 ; j <= N ; j++) {
                x[i][j] = numaratoare++;
            }
        }

        BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter("sat.cnf"));
        ArrayList<Clauza> clauze = new ArrayList<>();

        for(i = 1; i <= K ; i++) {
            Clauza clauza = new Clauza();
            for (int j = 1; j <= N ; j++) {
                clauza.getLiterali().add(x[i][j]);
            }
            clauze.add(clauza);
        }

        for (i = 1 ; i <= getK() ; i++) {
            for (int j = 1; j <= getK(); j++) {
                if( i != j) {
                    for( int k = 1; k <= getN() ; k++) {
                        //clauze.add(new Clauza(-x[i][k], -x[j][k]));
                        ArrayList<Integer> literali = new ArrayList<>();
                        literali.add(-x[i][k]);
                        literali.add(-x[j][k]);
                        clauze.add(new Clauza(literali));
                    }
                }
            }
        }

        for (i = 1 ;i <= getK() ; i++) {
            for(int k = 1; k <= getN(); k++) {
                for (int l = 1; l <= getN(); l++) {
                    if( l != k) {
                        //clauze.add(new Clauza(-x[i][k], -x[i][l]));
                        ArrayList<Integer> literali = new ArrayList<>();
                        literali.add(-x[i][k]);
                        literali.add(-x[i][l]);
                        clauze.add(new Clauza(literali));
                    }
                }
            }
        }
        //Clauze ca orice muchie sa aiba cel putin un varf in grup
        for(i = 1 ; i <= N ; i++) {
            for(int j = 1 ; j <= N ; j++) {
                if(matAdiacenta[i][j] == 1) {
                    ArrayList<Integer> literali = new ArrayList<>();
                    for(int k = 1; k <= K ; k++) {
                        literali.add(x[k][i]);
                        literali.add(x[k][j]);
                    }
                    clauze.add(new Clauza(literali));
                }
            }
        }

        StringBuilder stringBuilder = new StringBuilder();
        stringBuilder.append("p cnf ");
        stringBuilder.append(K*N);
        stringBuilder.append(" ");
        stringBuilder.append(clauze.size());
        stringBuilder.append("\n");
        for (Clauza clauza : clauze) {
            for(Integer lit: clauza.getLiterali()) {
                stringBuilder.append(lit);
                stringBuilder.append(" ");
            }
            stringBuilder.append(0);
            stringBuilder.append("\n");
        }
        stringBuilder.setLength(stringBuilder.length()-1);
        bufferedWriter.write(stringBuilder.toString());
        bufferedWriter.close();

    }

    @Override
    public void decipherOracleAnswer() throws IOException {
        BufferedReader bufferedReader = new BufferedReader(new FileReader("sat.sol"));
        String string;
        string = bufferedReader.readLine();
        if(string.compareTo("True") == 0) {
            solutie = true;
        }
        if(string.compareTo("False") == 0) {
            return;
        }

        string = bufferedReader.readLine();
        numarulVariabilelor = Integer.parseInt(string);
        string = bufferedReader.readLine();

        for(String str: string.split(" ")) {
            variabile.add(Integer.parseInt(str));
        }
        for(Integer var : variabile) {
            if( var > 0) {
                for(int i = 1; i <= getK(); i++) {
                    for (int j = 1; j <= getN(); j++) {
                        if(var.compareTo(x[i][j]) == 0) {
                            persoane.add(j);
                        }
                    }
                }
            }
        }
        persoane.sort(Comparator.naturalOrder());
    }

    @Override
    public void writeAnswer() throws IOException {
        OutputStreamWriter outputStreamWriter = new OutputStreamWriter(System.out);
        BufferedWriter bufferedWriter = new BufferedWriter(outputStreamWriter);
        StringBuilder stringBuilder = new StringBuilder();
        for(Integer i : persoane) {
            stringBuilder.append(i);
            stringBuilder.append(" ");
        }
        bufferedWriter.write(stringBuilder.toString());
        bufferedWriter.close();
    }
}
