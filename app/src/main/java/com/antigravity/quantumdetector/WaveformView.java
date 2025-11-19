package com.antigravity.quantumdetector;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;
import java.util.LinkedList;

public class WaveformView extends View {

    private Paint paint;
    private LinkedList<Float> dataPoints;
    private int maxPoints = 100;
    private float maxValue = 10.0f; // Default max value for scaling

    public WaveformView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        paint = new Paint();
        paint.setColor(Color.GREEN);
        paint.setStrokeWidth(5f);
        paint.setAntiAlias(true);
        paint.setStyle(Paint.Style.STROKE);
        dataPoints = new LinkedList<>();
    }

    public void addPoint(float value) {
        dataPoints.add(value);
        if (dataPoints.size() > maxPoints) {
            dataPoints.removeFirst();
        }
        invalidate(); // Request redraw
    }

    public void clear() {
        dataPoints.clear();
        invalidate();
    }

    public void setMaxValue(float max) {
        this.maxValue = max;
    }

    public void setColor(int color) {
        paint.setColor(color);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        if (dataPoints.size() < 2) return;

        int width = getWidth();
        int height = getHeight();
        float xStep = (float) width / (maxPoints - 1);

        float startX = 0;
        float startY = height - (dataPoints.get(0) / maxValue) * height;

        for (int i = 1; i < dataPoints.size(); i++) {
            float endX = i * xStep;
            float val = dataPoints.get(i);
            // Clamp value to avoid drawing off-screen
            if (val > maxValue) val = maxValue;
            float endY = height - (val / maxValue) * height;

            canvas.drawLine(startX, startY, endX, endY, paint);

            startX = endX;
            startY = endY;
        }
    }
}
