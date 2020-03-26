import com.google.gson.Gson;
import com.jmatio.io.MatFileReader;
import com.jmatio.types.MLChar;
import com.jmatio.types.MLDouble;
import com.jmatio.types.MLStructure;
import model.Point;
import util.Config;

import java.io.File;
import java.io.IOException;
import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

// Start Pat Additions
import org.influxdb.BatchOptions;
import org.influxdb.InfluxDB;
import org.influxdb.InfluxDBFactory;
import org.influxdb.dto.BatchPoints;
// import org.influxdb.dto.Point;

// End Pat Additions



public class Generator {
    private String db = "bearing";
    private static int BW = 256; // buffer window
    private static int MW = BW * 4; // merge window
    private static int FILE_SIZE = 20;
    private static int INTERVAL = 1;

    private static int LABEL_BASELINE = 0;
    private static int LABEL_OUTER_RACE_FAULT = 1;
    private static int LABEL_INNER_RACE_FAULT = 2;

    private static String ATTR_SR = "sr";
    private static String ATTR_GS = "gs";
    private static String ATTR_LOAD = "load";
    private static String ATTR_RATE = "rate";

    // Start Pat Additions
    private String host = "http://localhost:8086";
    private String username = "admin";
    private String password = "password";
    private String tsdb = "timeseriesdb";
    private InfluxDB influxDB;
    // End Pat Additions

    private String[] filenames = new String[] {
        "mats" + File.separator + "baseline_1.mat",
        "mats" + File.separator + "baseline_2.mat",
        "mats" + File.separator + "baseline_3.mat",

        "mats" + File.separator + "OuterRaceFault_1.mat",
        "mats" + File.separator + "OuterRaceFault_2.mat",
        "mats" + File.separator + "OuterRaceFault_3.mat",

        "mats" + File.separator + "InnerRaceFault_vload_1.mat",
        "mats" + File.separator + "InnerRaceFault_vload_2.mat",
        "mats" + File.separator + "InnerRaceFault_vload_3.mat",
        "mats" + File.separator + "InnerRaceFault_vload_4.mat",
        "mats" + File.separator + "InnerRaceFault_vload_5.mat",
        "mats" + File.separator + "InnerRaceFault_vload_6.mat",
        "mats" + File.separator + "InnerRaceFault_vload_7.mat",

        "mats" + File.separator + "OuterRaceFault_vload_1.mat",
        "mats" + File.separator + "OuterRaceFault_vload_2.mat",
        "mats" + File.separator + "OuterRaceFault_vload_3.mat",
        "mats" + File.separator + "OuterRaceFault_vload_4.mat",
        "mats" + File.separator + "OuterRaceFault_vload_5.mat",
        "mats" + File.separator + "OuterRaceFault_vload_6.mat",
        "mats" + File.separator + "OuterRaceFault_vload_7.mat"
    };

    private MLStructure[] readers = new MLStructure[FILE_SIZE];
    private int[] lengths = new int[FILE_SIZE];
    private double[] probs = new double[FILE_SIZE];
    private int totalLength;
    private Random random = new Random();
    private int[] cursors = new int[FILE_SIZE];
    private long timestamp;
    private Gson gson;
    private long interArrivalTime;

    public Generator() {
        gson = new Gson();
        interArrivalTime = Config.getInstance().getInterArrivalTime();
    }

    private void loadMatFiles() throws IOException {
        totalLength = 0;
        for (int i = 0; i < filenames.length; i++) {
            MatFileReader reader = new MatFileReader(filenames[i]);
            readers[i] = (MLStructure) reader.getMLArray(db);
            int len = readers[i].getField(ATTR_GS).getSize();
            lengths[i] = len - len % MW;
            totalLength += lengths[i];
            cursors[i] = 0;
        }

        probs[0] = lengths[0] * .1 / totalLength;
        for (int i = 1; i < probs.length; i++) {
            probs[i] = probs[i - 1] + lengths[i] * .1 / totalLength;
        }
    }

    // Start Pat Additions
    private void connect() {
        influxDB = InfluxDBFactory.connect(host, username, password);
        influxDB.setDatabase(tsdb);
        influxDB.enableBatch(BatchOptions.DEFAULTS.actions(BW).exceptionHandler(
                (failedPoints, throwable) -> throwable.printStackTrace())
        );
    }
    // End Pat Additions

    private int selectFile() {
        double prob = random.nextDouble();
        int min, max;

        if (prob < 0.7) {
            min = 0;
            max = 2;
        }
        else {
            min = 3;
            max = 19;
        }

        return ThreadLocalRandom.current().nextInt(min, max + 1);
    }

    private int generatePoints(int index, String metric) {
        int len = readers[index].getField(ATTR_GS).getSize();
        int start = cursors[index];
        int end = cursors[index] + MW;
        if (MW > len - cursors[index]) {
            cursors[index] = 0;
        }

        for (int i = start; i < end; i++ ) {
            model.Point point = new Point().withMetric(metric)
                                .withTimestamp(timestamp++)
                                .withLabel(getLabel(index))
                                .withSr(((MLDouble)readers[index].getField(ATTR_SR)).getArray()[0][0])
                                .withRate(((MLDouble)readers[index].getField(ATTR_RATE)).getArray()[0][0])
                                .withGs(((MLDouble)readers[index].getField(ATTR_GS)).getArray()[i][0]);

            if (readers[index].getField(ATTR_LOAD) instanceof MLChar) {
                point.setLoad(((MLChar) readers[index].getField(ATTR_LOAD)).getString(0));
            }
            else {
                point.setLoad(String.valueOf(((MLDouble) readers[index].getField(ATTR_LOAD)).getArray()[0][0]));
            }
            // Pat Change //
            // write the points to the influxdb
            org.influxdb.dto.Point point1 = org.influxdb.dto.Point.measurement("gear_metrics")
                .time(System.currentTimeMillis(), TimeUnit.MILLISECONDS)
                .addField("metric", metric) 
                .addField("label", getLabel(index))
                .addField("sr", ((MLDouble)readers[index].getField(ATTR_SR)).getArray()[0][0]) 
                .addField("rate", ((MLDouble)readers[index].getField(ATTR_RATE)).getArray()[0][0])
                .addField("gs", ((MLDouble)readers[index].getField(ATTR_GS)).getArray()[i][0])
                .addField("load", point.getLoad())
                .addField("ts", point.getTimestamp())
                .build();
            
            // End Pat Change //
            influxDB.write(point1);
            output(point);
        }

        return MW;
    }

    private void output(Point point) {
        System.out.println(gson.toJson(point));
    }

    private int getLabel(int index) {
        if (index < 3)
            return LABEL_BASELINE;
        else if (index < 6)
            return LABEL_OUTER_RACE_FAULT;
        else if (index < 13)
            return LABEL_INNER_RACE_FAULT;
        else
            return LABEL_OUTER_RACE_FAULT;
    }

    private int getInterArrivalOffset() {
        return (random.nextInt(21) - 10) * 10;
    }

    public void startOffline() {
        int offlineCount = 0;
        int offlineTotal = totalLength / 2;
        timestamp = 0;
        while (offlineCount < offlineTotal) {
            int index = selectFile();
            offlineCount += generatePoints(index, "offline");
            try {
                Thread.sleep(interArrivalTime + getInterArrivalOffset());
            } catch (InterruptedException ignored) {}
        }
    }

    public void startOnline() {
        timestamp = 0;
        while (true) {
            int index = selectFile();
            generatePoints(index, "online");
            try {
                Thread.sleep(interArrivalTime + getInterArrivalOffset());
            } catch (InterruptedException ignored) {}
        }
    }

    public static void main(String[] args) {
        Generator generator = new Generator();

        try {
            generator.loadMatFiles();
        } catch (IOException e) {
            e.printStackTrace();
            return;
        }

        generator.connect();


        if (args.length > 0) {
            switch (args[0]) {
                case "-offline":
                    generator.startOffline();
                    break;
                case "-online":
                    generator.startOnline();
                    break;
                case "-all":
                    generator.startOffline();
                    generator.startOnline();
                    break;
                default:
                    System.out.println("Usage: datagen [-offline | -online | -all]");
                    break;
            }
        }
        else {
            generator.startOffline();
            generator.startOnline();
        }
    }
}
