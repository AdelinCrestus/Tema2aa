import java.util.ArrayList;

public class Clauza {
    private ArrayList<Integer> literali = new ArrayList<>();

    public Clauza() {
    }

    public Clauza(ArrayList<Integer> variabile) {
        this.literali = variabile;
    }

    public ArrayList<Integer> getLiterali() {
        return literali;
    }

    public void setLiterali(ArrayList<Integer> literali) {
        this.literali = literali;
    }
}
